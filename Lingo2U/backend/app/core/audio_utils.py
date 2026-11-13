from fastapi import HTTPException

MAX_DURATION_SECONDS = 30.0
BLOCKED_TERMS = {"ignore previous instructions", "system prompt", "reveal your instructions"}


def validate_audio_duration(audio_bytes: bytes, duration_header: float | None = None) -> None:
    if duration_header is not None and duration_header > MAX_DURATION_SECONDS:
        raise HTTPException(
            status_code=400,
            detail={"error": "AUDIO_TOO_LONG", "message": "Audio clip must be 30 seconds or less."},
        )
    if len(audio_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail={"error": "AUDIO_TOO_LARGE", "message": "Audio file exceeds 5 MB limit."},
        )


def sanitize_and_moderate_text(text: str) -> str:
    cleaned = text.strip()
    lowered = cleaned.lower()
    for term in BLOCKED_TERMS:
        if term in lowered:
            raise HTTPException(
                status_code=400,
                detail={"error": "UNSAFE_INPUT", "message": "Please stay within the English practice conversation."},
            )
    return cleaned[:500]
