from typing import Literal, TypedDict
from pydantic import BaseModel, Field


class ScenarioConfig(TypedDict):
    id: str
    title: str
    tutor_role: str
    goal: str
    target_vocab: list[str]
    target_patterns: list[str]


class LearnerProfile(TypedDict):
    level: str
    native_language: str
    explain_in_native: bool


class ChatTurn(TypedDict):
    role: Literal["user", "tutor"]
    content: str


class UnderstandResult(BaseModel):
    intent: Literal["on_topic", "off_topic", "unclear", "needs_help", "repeat"] = Field(
        description="Classification of the learner's input"
    )


class CorrectionOutput(BaseModel):
    has_error: bool = Field(description="True only if the learner made a grammar or vocabulary error")
    original: str = ""
    corrected: str = ""
    reason: str = Field(default="", description="Simple A1-A2 explanation, max 20 words")
    error_type: Literal["tense", "article", "preposition", "word_order", "vocabulary", "other", "none"] = "none"
    native_explanation: str | None = None


class LevelGuardOutput(BaseModel):
    is_beginner_safe: bool
    rewritten_reply: str = Field(
        description="A1-A2 compliant reply: max 2 short sentences + 1 simple question"
    )


class TutorState(TypedDict):
    session_id: str
    scenario: ScenarioConfig
    learner: LearnerProfile
    history: list[ChatTurn]
    user_text: str
    correction: dict | None
    tutor_reply: str
    flags: dict
