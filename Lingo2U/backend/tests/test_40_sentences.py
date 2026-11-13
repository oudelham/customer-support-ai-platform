import pytest
from unittest.mock import AsyncMock, patch
from app.ai.graph.builder import tutor_graph
from app.ai.graph.report_graph import report_graph
from app.ai.graph.state import CorrectionOutput, UnderstandResult

LEARNER_EVAL_SET = [
    ("My name is Lucas.", "on_topic", False),
    ("I am from Brazil.", "on_topic", False),
    ("I live in Sao Paulo.", "on_topic", False),
    ("I like play football.", "on_topic", True),
    ("My hobby are music.", "on_topic", True),
    ("Nice to meet you.", "on_topic", False),
    ("I have twenty years old.", "on_topic", True),
    ("Can I have a coffee, please?", "on_topic", False),
    ("I would like a sandwich.", "on_topic", False),
    ("How much it is?", "on_topic", True),
    ("Give me water cold.", "on_topic", True),
    ("Can I have the bill, please?", "on_topic", False),
    ("I want eat salad.", "on_topic", True),
    ("Do you have this in medium?", "on_topic", False),
    ("I am looking for a blue jacket.", "on_topic", False),
    ("How much cost this shirt?", "on_topic", True),
    ("Can I try it on?", "on_topic", False),
    ("It is too much big.", "on_topic", True),
    ("She wear black shoes.", "on_topic", True),
    ("I wake up at seven o'clock.", "on_topic", False),
    ("In the morning I drink tea.", "on_topic", False),
    ("He go to work by bus.", "on_topic", True),
    ("Yesterday I go to the market.", "on_topic", True),
    ("I go to bed at ten.", "on_topic", False),
    ("After work I watches TV.", "on_topic", True),
    ("Excuse me, where is the bank?", "on_topic", False),
    ("How do I get to train station?", "on_topic", True),
    ("Is it far from here?", "on_topic", False),
    ("Turn left at the pharmacy.", "on_topic", False),
    ("The bank is near to the hotel.", "on_topic", True),
    ("How was your weekend?", "on_topic", False),
    ("I have a meeting at two.", "on_topic", False),
    ("I am working in a project.", "on_topic", True),
    ("Can you help me with this email?", "on_topic", False),
    ("Yesterday I send the report.", "on_topic", True),
    ("I am ready for the meeting.", "on_topic", False),
    ("What is the capital of Mars?", "off_topic", False),
    ("Tell me about quantum physics.", "off_topic", False),
    ("Can you write Python code for me?", "off_topic", False),
    ("Who won the football game in 1998?", "off_topic", False),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("sentence,intent,has_error", LEARNER_EVAL_SET)
async def test_40_learner_sentences(sentence: str, intent: str, has_error: bool):
    u_res = UnderstandResult(intent=intent)
    c_res = CorrectionOutput(
        has_error=has_error,
        original=sentence,
        corrected="Corrected version." if has_error else sentence,
        reason="Simple grammar reason under twenty words." if has_error else "",
        error_type="grammar" if has_error else "none",
    )
    reply_msg = AsyncMock()
    reply_msg.content = "Good job! Let us continue our cafe practice. What drink would you like?"

    with patch("app.ai.graph.nodes.get_llm_provider") as mock_llm:
        inst = mock_llm.return_value
        inst.get_structured_model.side_effect = [
            AsyncMock(ainvoke=AsyncMock(return_value=u_res)),
            AsyncMock(ainvoke=AsyncMock(return_value=c_res)),
        ]
        inst.get_chat_model.return_value = AsyncMock(ainvoke=AsyncMock(return_value=reply_msg))

        out = await tutor_graph.ainvoke({
            "session_id": "s1",
            "scenario": {
                "id": "1",
                "title": "Ordering Food",
                "tutor_role": "Waiter",
                "goal": "Order a meal",
                "target_vocab": ["coffee", "water"],
                "target_patterns": ["Can I have...?"],
            },
            "learner": {"level": "A1", "native_language": "Spanish", "explain_in_native": False},
            "history": [],
            "user_text": sentence,
            "correction": None,
            "tutor_reply": "",
            "flags": {},
        })

        assert out["flags"]["off_topic"] is (intent == "off_topic")
        assert out["tutor_reply"].count("?") == 1
        assert (out["correction"] is not None) is has_error


@pytest.mark.asyncio
async def test_short_session_produces_good_start_message():
    res = await report_graph.ainvoke({
        "scenario_title": "Introductions",
        "target_vocab": ["name", "from"],
        "user_turns": ["Hello!"],
        "corrections": [],
        "ranked_mistakes": [],
        "report": {},
    })
    assert "Good start!" in res["report"]["summary"]
