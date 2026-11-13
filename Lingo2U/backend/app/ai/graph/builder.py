from langgraph.graph import END, START, StateGraph
from app.ai.graph.state import TutorState
from app.ai.graph.nodes import (
    check_grammar_node,
    finalize_node,
    generate_reply_node,
    level_guard_node,
    translate_explanation_node,
    understand_node,
)


def build_tutor_graph():
    builder = StateGraph(TutorState)

    builder.add_node("understand", understand_node)
    builder.add_node("check_grammar", check_grammar_node)
    builder.add_node("generate_reply", generate_reply_node)
    builder.add_node("level_guard", level_guard_node)
    builder.add_node("translate_explanation", translate_explanation_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "understand")
    builder.add_edge("understand", "check_grammar")
    builder.add_edge("understand", "generate_reply")

    builder.add_edge("generate_reply", "level_guard")
    builder.add_edge("check_grammar", "translate_explanation")

    builder.add_edge("level_guard", "finalize")
    builder.add_edge("translate_explanation", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()


tutor_graph = build_tutor_graph()
