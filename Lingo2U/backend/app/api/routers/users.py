from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.models import MistakeStat, Session, User, UserProfile, UserProgress
from app.db.session import get_db

router = APIRouter(prefix="/users", tags=["users"])


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    native_language: str | None = Field(default=None, max_length=50)
    goal: str | None = Field(default=None, max_length=50)
    level: str | None = Field(default=None, pattern="^(A1|A2)$")
    explain_in_native: bool | None = None
    onboarding_completed: bool | None = None


@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": profile.display_name if profile else "",
        "native_language": profile.native_language if profile else "English",
        "goal": profile.goal if profile else "daily_life",
        "level": profile.level if profile else "A1",
        "explain_in_native": profile.explain_in_native if profile else False,
        "onboarding_completed": profile.onboarding_completed if profile else False,
    }


@router.put("/me")
async def update_me(
    payload: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    return await get_me(user, db)


@router.delete("/me/transcripts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_transcripts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.execute(delete(MistakeStat).where(MistakeStat.user_id == user.id))
    progress = await db.scalar(select(UserProgress).where(UserProgress.user_id == user.id))
    if progress:
        progress.completed_sessions = 0
        progress.total_seconds = 0
        progress.last_session_at = None
    await db.commit()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.delete(user)
    await db.commit()
