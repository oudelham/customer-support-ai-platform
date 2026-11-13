from datetime import datetime, timezone
import time
import uuid
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.ai.graph.builder import tutor_graph
from app.ai.graph.report_graph import report_graph
from app.ai.providers.stt import get_stt_provider
from app.ai.providers.tts import get_tts_provider
from app.core.audio_utils import sanitize_and_moderate_text, validate_audio_duration
from app.core.rate_limit import check_daily_turn_limit, check_idempotency
from app.db.models import (
    Correction,
    Message,
    MistakeStat,
    Scenario,
    Session,
    SessionReport,
    User,
    UserProfile,
    UserProgress,
)
from app.db.session import get_db

router = APIRouter(prefix="/sessions", tags=["sessions"])

ALLOWED_AUDIO_TYPES = {"audio/webm", "audio/mp4", "audio/mpeg", "audio/wav", "audio/ogg"}


class StartSessionRequest(BaseModel):
    scenario_id: uuid.UUID


class TextTurnRequest(BaseModel):
    text: str


class SlowTTSRequest(BaseModel):
    text: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_session(
    payload: StartSessionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scenario = await db.get(Scenario, payload.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Scenario not found."})

    session = Session(user_id=user.id, scenario_id=scenario.id, status="active")
    db.add(session)
    await db.flush()

    greeting = f"Hello! Welcome to {scenario.title}. {scenario.target_patterns[0]} What about you?"
    if scenario.slug == "ordering-food":
        greeting = "Hello! Welcome to our cafe. What would you like to eat or drink today?"
    elif scenario.slug == "introductions":
        greeting = "Hi there! My name is Sam. What is your name?"

    tutor_msg = Message(session_id=session.id, role="tutor", content=greeting, input_mode="text")
    db.add(tutor_msg)
    await db.commit()

    audio_b64 = await get_tts_provider().synthesize_base64(greeting)
    return {
        "session_id": str(session.id),
        "scenario": {
            "id": str(scenario.id),
            "title": scenario.title,
            "goal": scenario.goal,
            "tutor_role": scenario.tutor_role,
            "target_vocab": scenario.target_vocab,
        },
        "greeting": greeting,
        "audio_base64": audio_b64,
    }


async def _process_learner_turn(
    session: Session,
    user: User,
    user_text: str,
    input_mode: str,
    db: AsyncSession,
) -> dict:
    t0 = time.perf_counter()
    clean_text = sanitize_and_moderate_text(user_text)
    scenario = await db.get(Scenario, session.scenario_id)
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))

    past_msgs = (
        await db.scalars(
            select(Message).where(Message.session_id == session.id).order_by(Message.created_at.asc())
        )
    ).all()
    history = [{"role": m.role, "content": m.content} for m in past_msgs[-10:]]

    user_msg = Message(session_id=session.id, role="user", content=clean_text, input_mode=input_mode)
    db.add(user_msg)
    await db.flush()

    graph_state = {
        "session_id": str(session.id),
        "scenario": {
            "id": str(scenario.id),
            "title": scenario.title,
            "tutor_role": scenario.tutor_role,
            "goal": scenario.goal,
            "target_vocab": scenario.target_vocab,
            "target_patterns": scenario.target_patterns,
        },
        "learner": {
            "level": profile.level if profile else "A1",
            "native_language": profile.native_language if profile else "English",
            "explain_in_native": profile.explain_in_native if profile else False,
        },
        "history": history,
        "user_text": clean_text,
        "correction": None,
        "tutor_reply": "",
        "flags": {},
    }

    result = await tutor_graph.ainvoke(graph_state)
    correction_data = result.get("correction")
    tutor_reply = result["tutor_reply"]

    if correction_data:
        db.add(
            Correction(
                message_id=user_msg.id,
                original=correction_data["original"],
                corrected=correction_data["corrected"],
                reason=correction_data["reason"],
                error_type=correction_data["error_type"],
                native_explanation=correction_data.get("native_explanation"),
            )
        )
        stat = await db.scalar(
            select(MistakeStat).where(
                MistakeStat.user_id == user.id,
                MistakeStat.error_type == correction_data["error_type"],
            )
        )
        if stat:
            stat.count += 1
        else:
            db.add(MistakeStat(user_id=user.id, error_type=correction_data["error_type"], count=1))

    tutor_msg = Message(session_id=session.id, role="tutor", content=tutor_reply, input_mode="text")
    db.add(tutor_msg)
    await db.commit()

    audio_b64 = await get_tts_provider().synthesize_base64(tutor_reply)
    latency_ms = round((time.perf_counter() - t0) * 1000)

    return {
        "transcript": clean_text,
        "tutor_text": tutor_reply,
        "correction": correction_data,
        "audio_base64": audio_b64,
        "latency_ms": latency_ms,
    }


@router.post("/{session_id}/messages")
async def submit_text_turn(
    session_id: uuid.UUID,
    payload: TextTurnRequest,
    x_idempotency_key: str | None = Header(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_idempotency(x_idempotency_key)
    check_daily_turn_limit(str(user.id))

    session = await db.scalar(select(Session).where(Session.id == session_id, Session.user_id == user.id))
    if not session or session.status != "active":
        raise HTTPException(status_code=404, detail={"error": "SESSION_INVALID", "message": "Active session not found."})

    return await _process_learner_turn(session, user, payload.text, "text", db)


@router.post("/{session_id}/voice")
async def submit_voice_turn(
    session_id: uuid.UUID,
    audio: UploadFile = File(...),
    x_idempotency_key: str | None = Header(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_idempotency(x_idempotency_key)
    check_daily_turn_limit(str(user.id))

    session = await db.scalar(select(Session).where(Session.id == session_id, Session.user_id == user.id))
    if not session or session.status != "active":
        raise HTTPException(status_code=404, detail={"error": "SESSION_INVALID", "message": "Active session not found."})

    content_type = (audio.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail={"error": "INVALID_AUDIO_TYPE", "message": "Unsupported audio format."})

    audio_bytes = await audio.read()
    validate_audio_duration(audio_bytes)

    transcript = await get_stt_provider().transcribe(audio_bytes, audio.filename or "speech.webm")
    if not transcript:
        return {
            "transcript": "",
            "tutor_text": "I could not hear anything. Please hold the microphone button and try again, or type below.",
            "correction": None,
            "audio_base64": None,
        }

    return await _process_learner_turn(session, user, transcript, "voice", db)


@router.post("/{session_id}/help")
async def get_help_samples(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.scalar(select(Session).where(Session.id == session_id, Session.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Session not found."})
    scenario = await db.get(Scenario, session.scenario_id)
    return {"samples": scenario.target_patterns[:3]}


@router.post("/{session_id}/slow-tts")
async def get_slow_audio(
    session_id: uuid.UUID,
    payload: SlowTTSRequest,
    _: User = Depends(get_current_user),
):
    audio_b64 = await get_tts_provider().synthesize_base64(payload.text, slow=True)
    return {"audio_base64": audio_b64}


@router.post("/{session_id}/end")
async def end_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.scalar(select(Session).where(Session.id == session_id, Session.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Session not found."})

    existing_report = await db.scalar(select(SessionReport).where(SessionReport.session_id == session.id))
    if existing_report:
        return existing_report.report_json

    now = datetime.now(timezone.utc)
    session.ended_at = now
    session.status = "completed"
    session.duration_seconds = max(1, int((now - session.started_at).total_seconds()))

    scenario = await db.get(Scenario, session.scenario_id)
    msgs = (
        await db.scalars(
            select(Message).where(Message.session_id == session.id).order_by(Message.created_at.asc())
        )
    ).all()

    user_turns = [m.content for m in msgs if m.role == "user"]
    msg_ids = [m.id for m in msgs if m.role == "user"]
    corrections_rows = (
        await db.scalars(select(Correction).where(Correction.message_id.in_(msg_ids)))
    ).all() if msg_ids else []

    corrections_list = [
        {"wrong": c.original, "right": c.corrected, "why": c.reason}
        for c in corrections_rows
    ]

    graph_out = await report_graph.ainvoke({
        "scenario_title": scenario.title if scenario else "Practice",
        "target_vocab": scenario.target_vocab if scenario else [],
        "user_turns": user_turns,
        "corrections": corrections_list,
        "ranked_mistakes": [],
        "report": {},
    })
    report_payload = graph_out["report"]

    db.add(
        SessionReport(
            session_id=session.id,
            summary=report_payload["summary"],
            report_json=report_payload,
        )
    )

    progress = await db.scalar(select(UserProgress).where(UserProgress.user_id == user.id))
    if progress:
        progress.completed_sessions += 1
        progress.total_seconds += session.duration_seconds
        progress.last_session_at = now

    await db.commit()
    return report_payload


@router.get("")
async def list_user_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(Session, Scenario)
            .join(Scenario, Session.scenario_id == Scenario.id)
            .where(Session.user_id == user.id)
            .order_by(Session.started_at.desc())
        )
    ).all()

    return [
        {
            "id": str(sess.id),
            "scenario_title": scen.title,
            "started_at": sess.started_at.isoformat(),
            "duration_seconds": sess.duration_seconds,
            "status": sess.status,
        }
        for sess, scen in rows
    ]


@router.get("/{session_id}")
async def get_session_detail(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.scalar(select(Session).where(Session.id == session_id, Session.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Session not found."})

    scenario = await db.get(Scenario, session.scenario_id)
    msgs = (
        await db.scalars(
            select(Message).where(Message.session_id == session.id).order_by(Message.created_at.asc())
        )
    ).all()

    msg_ids = [m.id for m in msgs]
    corr_rows = (
        await db.scalars(select(Correction).where(Correction.message_id.in_(msg_ids)))
    ).all() if msg_ids else []
    corr_map = {c.message_id: c for c in corr_rows}

    report = await db.scalar(select(SessionReport).where(SessionReport.session_id == session.id))

    return {
        "id": str(session.id),
        "status": session.status,
        "duration_seconds": session.duration_seconds,
        "scenario": {
            "id": str(scenario.id),
            "title": scenario.title,
            "goal": scenario.goal,
        },
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "input_mode": m.input_mode,
                "correction": {
                    "original": corr_map[m.id].original,
                    "corrected": corr_map[m.id].corrected,
                    "reason": corr_map[m.id].reason,
                    "error_type": corr_map[m.id].error_type,
                    "native_explanation": corr_map[m.id].native_explanation,
                }
                if m.id in corr_map
                else None,
            }
            for m in msgs
        ],
        "report": report.report_json if report else None,
    }
