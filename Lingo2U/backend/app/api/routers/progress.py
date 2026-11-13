from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.models import MistakeStat, User, UserProgress
from app.db.session import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("")
async def get_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    progress = await db.scalar(select(UserProgress).where(UserProgress.user_id == user.id))
    mistakes = (
        await db.scalars(
            select(MistakeStat)
            .where(MistakeStat.user_id == user.id)
            .order_by(MistakeStat.count.desc())
        )
    ).all()

    total_seconds = progress.total_seconds if progress else 0
    return {
        "completed_sessions": progress.completed_sessions if progress else 0,
        "total_minutes": round(total_seconds / 60, 1),
        "last_session_at": progress.last_session_at.isoformat() if progress and progress.last_session_at else None,
        "mistake_trends": [{"error_type": m.error_type, "count": m.count} for m in mistakes],
    }
