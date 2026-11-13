from typing import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import END, START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from app.ai.providers.llm import get_llm_provider


class MistakeItem(BaseModel):
    wrong: str
    right: str
    why: str


class VocabItem(BaseModel):
    word: str
    meaning: str
    example: str


class SessionReportSchema(BaseModel):
    summary: str
    top_mistakes: list[MistakeItem] = Field(default_factory=list, max_length=3)
    new_words: list[VocabItem] = Field(default_factory=list, max_length=5)
    strengths: str
    next_tip: str


class ReportState(TypedDict):
    scenario_title: str
    target_vocab: list[str]
    user_turns: list[str]
    corrections: list[dict]
    ranked_mistakes: list[dict]
    report: dict


async def collect_node(state: ReportState) -> dict:
    return state


async def rank_mistakes_node(state: ReportState) -> dict:
    corrections = state.get("corrections", [])
    return {"ranked_mistakes": corrections[:3]}


async def write_report_node(state: ReportState) -> dict:
    if len(state["user_turns"]) < 2:
        return {
            "report": {
                "summary": "Good start! Practice a few more sentences next time to unlock a full feedback report.",
                "top_mistakes": [],
                "new_words": [],
                "strengths": "You started your conversation with Sam!",
                "next_tip": "Try completing at least 3 turns in your next scenario.",
            }
        }

    llm = get_llm_provider().get_structured_model(SessionReportSchema)
    prompt = (
        f"Scenario: {state['scenario_title']}\n"
        f"Target Vocabulary: {', '.join(state['target_vocab'][:5])}\n"
        f"Learner Sentences: {state['user_turns']}\n"
        f"Top Corrections: {state['ranked_mistakes']}\n"
        "Write an encouraging A1-A2 beginner session report with at most 3 mistakes and up to 5 new words."
    )
    res: SessionReportSchema = await llm.ainvoke([
        SystemMessage(content="You are Sam, creating a simple A1-A2 end-of-session report."),
        HumanMessage(content=prompt),
    ])
    return {"report": res.model_dump()}


def build_report_graph():
    builder = StateGraph(ReportState)
    builder.add_node("collect", collect_node)
    builder.add_node("rank_mistakes", rank_mistakes_node)
    builder.add_node("write_report", write_report_node)

    builder.add_edge(START, "collect")
    builder.add_edge("collect", "rank_mistakes")
    builder.add_edge("rank_mistakes", "write_report")
    builder.add_edge("write_report", END)
    return builder.compile()


report_graph = build_report_graph()
