"""그래프 조립.

목표 구조:

    START -> retrieve ─┬─ 차단됨 ────────────────────→ answer -> END
                       └─ 정상 → generate → execute ─┬─ 성공 → answer
                                      ↑              └─ 실패 ┘
                                      └──────────────────────┘

프로젝트 1과 달라지는 것은 retrieve 뒤의 분기 하나뿐입니다.
"이 DB에 없는 정보면 SQL 을 아예 만들지 않는다" — 비용도 아끼고 환각도 막습니다.

실행:
    ..\\.venv\\Scripts\\python.exe -m src.agent.graph
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agent.nodes import (
    answer_node,
    execute_node,
    generate_node,
    retrieve_node,
    route_after_execute,
    route_after_retrieve,
)
from src.agent.state import AgentState


def build_graph():
    """TODO: 아래 뼈대를 완성하세요.

    builder = StateGraph(AgentState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_node("execute", execute_node)
    builder.add_node("answer", answer_node)

    builder.add_edge(START, "retrieve")
    builder.add_conditional_edges(
        "retrieve", route_after_retrieve,
        {"blocked": "answer", "generate": "generate"},
    )
    builder.add_edge("generate", "execute")
    builder.add_conditional_edges(
        "execute", route_after_execute,
        {"retry": "generate", "answer": "answer"},
    )
    builder.add_edge("answer", END)

    return builder.compile()
    """
    raise NotImplementedError  # TODO


def ask(question: str) -> dict:
    """편의 함수. 초기 상태를 채워 그래프를 실행한다.

    TODO: attempts=0, error=None 을 반드시 초기값으로 넣으세요.
          안 넣으면 노드에서 KeyError 가 납니다.
    """
    graph = build_graph()
    return graph.invoke({"question": question, "attempts": 0, "error": None})


if __name__ == "__main__":
    graph = build_graph()
    print(graph.get_graph().draw_mermaid())   # mermaid.live 에 붙여 그림으로 확인

    result = ask("작년 국가별 매출 상위 5개국 알려줘")
    print("\nSQL:\n", result.get("sql"))
    print("\n답변:\n", result.get("answer"))
