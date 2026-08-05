"""LangGraph 상태 정의.

**그래프 설계는 상태 설계가 8할입니다.** 노드를 짜기 전에 여기부터 채우세요.

프로젝트 1의 SQLState 에서 달라지는 점:
    - schema(문자열) 대신 온톨로지 조각들을 담는다
    - blocked_reason 이 생긴다 (미보유 주제면 SQL 생성 자체를 건너뜀)
"""

from __future__ import annotations

from typing import Optional, TypedDict


class AgentState(TypedDict):
    # --- 입력 ---
    question: str

    # --- 검색 단계 ---
    # TODO: 아래를 채우세요
    #   entities: list[str]         검색된 엔티티 이름들
    #   metrics: list[str]          검색된 지표 이름들
    #   context: str                compiler.render_context() 결과
    #   join_sql: str               compiler.build_join_sql() 결과
    #   blocked_reason: Optional[str]

    # --- 생성/실행 단계 ---
    # TODO:
    #   sql: str
    #   error: Optional[str]
    #   df: object                  pandas DataFrame
    #   attempts: int

    # --- 출력 ---
    answer: str
