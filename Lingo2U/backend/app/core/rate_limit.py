from datetime import date
from fastapi import HTTPException, status
from app.core.config import settings

_daily_counts: dict[tuple[str, date], int] = {}
_seen_idempotency_keys: set[str] = set()


def check_daily_turn_limit(user_id: str) -> None:
    key = (user_id, date.today())
    current = _daily_counts.get(key, 0)
    if current >= settings.DAILY_TURN_CAP:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "DAILY_LIMIT_REACHED",
                "message": "You have reached your daily practice limit. Come back tomorrow!",
            },
        )
    _daily_counts[key] = current + 1


def check_idempotency(idempotency_key: str | None) -> None:
    if not idempotency_key:
        return
    if idempotency_key in _seen_idempotency_keys:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "DUPLICATE_TURN", "message": "This turn was already submitted."},
        )
    _seen_idempotency_keys.add(idempotency_key)
