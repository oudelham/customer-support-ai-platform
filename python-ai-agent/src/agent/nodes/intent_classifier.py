from pydantic import BaseModel, Field
from src.agent.model import get_model
from src.agent.prompts import INTENT_PROMPT


class IntentResult(BaseModel):
    intent: str = Field(description="support, billing, technical, or escalation")
    confidence: float = Field(ge=0, le=1)


async def classify_intent(state: dict):
    model = get_model().with_structured_output(IntentResult)
    result = await model.ainvoke([
        {"role": "system", "content": INTENT_PROMPT},
        {"role": "user", "content": state["user_input"]},
    ])
    return {
        "intent": result.intent,
        "confidence": result.confidence,
        "requires_human": result.intent == "escalation" or result.confidence < 0.60,
    }
