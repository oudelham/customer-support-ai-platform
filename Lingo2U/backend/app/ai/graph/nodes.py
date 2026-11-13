from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage
from app.ai.graph.state import (
    CorrectionOutput,
    LevelGuardOutput,
    TutorState,
    UnderstandResult,
)
from app.ai.providers.llm import get_llm_provider

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
TUTOR_PROMPT = (PROMPTS_DIR / "tutor_system.md").read_text(encoding="utf-8")
CORRECTION_PROMPT = (PROMPTS_DIR / "correction.md").read_text(encoding="utf-8")


async def understand_node(state: TutorState) -> dict:
    user_text = state["user_text"].strip()
    if not user_text:
        return {"flags": {"intent": "unclear", "off_topic": False}}

    llm = get_llm_provider().get_structured_model(UnderstandResult)
    sys_msg = (
        f"Scenario: {state['scenario']['title']} ({state['scenario']['goal']}). "
        "Classify the learner's response inside <learner_input> as: "
        "'on_topic', 'off_topic', 'unclear' (gibberish/unintelligible), "
        "'needs_help' (asking what to say), or 'repeat' (asking to repeat)."
    )
    result: UnderstandResult = await llm.ainvoke([
        SystemMessage(content=sys_msg),
        HumanMessage(content=f"<learner_input>{user_text}</learner_input>"),
    ])
    return {
        "flags": {
            "intent": result.intent,
            "off_topic": result.intent == "off_topic",
            "unclear": result.intent == "unclear",
            "needs_help": result.intent == "needs_help",
        }
    }


async def check_grammar_node(state: TutorState) -> dict:
    intent = state.get("flags", {}).get("intent", "on_topic")
    if intent in ("unclear", "needs_help", "repeat"):
        return {"correction": None}

    llm = get_llm_provider().get_structured_model(CorrectionOutput)
    result: CorrectionOutput = await llm.ainvoke([
        SystemMessage(content=CORRECTION_PROMPT),
        HumanMessage(content=f"<learner_input>{state['user_text']}</learner_input>"),
    ])

    if not result.has_error or result.corrected.strip().lower() == state["user_text"].strip().lower():
        return {"correction": None}

    words = result.reason.split()
    trimmed_reason = " ".join(words[:20])

    return {
        "correction": {
            "original": state["user_text"],
            "corrected": result.corrected,
            "reason": trimmed_reason,
            "error_type": result.error_type if result.error_type != "none" else "other",
            "native_explanation": None,
        }
    }


async def generate_reply_node(state: TutorState) -> dict:
    intent = state.get("flags", {}).get("intent", "on_topic")
    scenario = state["scenario"]

    if intent == "unclear":
        return {
            "tutor_reply": "I did not hear that clearly. Could you try saying it again?"
        }
    if intent == "needs_help":
        examples = ", or ".join(f"'{p}'" for p in scenario["target_patterns"][:2])
        return {
            "tutor_reply": f"No problem! You can try saying {examples}. Want to try one?"
        }

    llm = get_llm_provider().get_chat_model(temperature=0.5)
    formatted_system = TUTOR_PROMPT.format(
        scenario_title=scenario["title"],
        tutor_role=scenario["tutor_role"],
        scenario_goal=scenario["goal"],
        target_vocab=", ".join(scenario["target_vocab"]),
        target_patterns=", ".join(scenario["target_patterns"]),
        learner_level=state["learner"]["level"],
        off_topic=state.get("flags", {}).get("off_topic", False),
    )

    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in state["history"][-8:]
    )
    user_prompt = (
        f"Recent conversation:\n{history_text}\n\n"
        f"<learner_input>{state['user_text']}</learner_input>\n"
        "Respond as Sam (max 2 short sentences + 1 simple question):"
    )

    response = await llm.ainvoke([
        SystemMessage(content=formatted_system),
        HumanMessage(content=user_prompt),
    ])
    return {"tutor_reply": str(response.content).strip()}


async def level_guard_node(state: TutorState) -> dict:
    reply = state["tutor_reply"]
    sentences = [s.strip() for s in reply.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    question_count = reply.count("?")
    max_words_in_sentence = max((len(s.split()) for s in sentences), default=0)

    if len(sentences) <= 3 and question_count == 1 and max_words_in_sentence <= 15:
        return {"tutor_reply": reply}

    llm = get_llm_provider().get_structured_model(LevelGuardOutput)
    result: LevelGuardOutput = await llm.ainvoke([
        SystemMessage(
            content=(
                "Rewrite this English tutor reply for an A1-A2 beginner. "
                "Rules: Maximum 2 short, simple sentences followed by EXACTLY 1 simple question. "
                "Use only common everyday words."
            )
        ),
        HumanMessage(content=reply),
    ])
    return {"tutor_reply": result.rewritten_reply}


async def translate_explanation_node(state: TutorState) -> dict:
    correction = state.get("correction")
    learner = state["learner"]
    if not correction or not learner.get("explain_in_native"):
        return {}

    native_lang = learner.get("native_language", "English")
    if native_lang.lower() == "english":
        return {}

    llm = get_llm_provider().get_chat_model(temperature=0.2)
    res = await llm.ainvoke([
        SystemMessage(
            content=f"Translate this short grammar explanation into {native_lang}. Keep it brief and beginner-friendly."
        ),
        HumanMessage(content=correction["reason"]),
    ])
    updated = dict(correction)
    updated["native_explanation"] = str(res.content).strip()
    return {"correction": updated}


async def finalize_node(state: TutorState) -> dict:
    return state
