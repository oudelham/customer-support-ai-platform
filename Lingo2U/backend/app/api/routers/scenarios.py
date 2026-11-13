import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.models import Scenario, User
from app.db.session import get_db

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("")
async def list_scenarios(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scenarios = (
        await db.scalars(select(Scenario).order_by(Scenario.sort_order.asc()))
    ).all()
    return [
        {
            "id": str(s.id),
            "slug": s.slug,
            "title": s.title,
            "description": s.description,
            "difficulty": s.difficulty,
            "tutor_role": s.tutor_role,
            "goal": s.goal,
            "target_vocab": s.target_vocab,
            "target_patterns": s.target_patterns,
            "suggested_turns": s.suggested_turns,
        }
        for s in scenarios
    ]


@router.get("/{scenario_id}")
async def get_scenario(
    scenario_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s = await db.get(Scenario, scenario_id)
    if not s:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Scenario not found."})
    return {
        "id": str(s.id),
        "slug": s.slug,
        "title": s.title,
        "description": s.description,
        "difficulty": s.difficulty,
        "tutor_role": s.tutor_role,
        "goal": s.goal,
        "target_vocab": s.target_vocab,
        "target_patterns": s.target_patterns,
        "suggested_turns": s.suggested_turns,
    }
