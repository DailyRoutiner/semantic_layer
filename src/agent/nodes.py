"""그래프 노드들.

각 노드는 상태를 읽고 **바뀐 부분만** dict 로 반환합니다.
노드 안에서 예외를 던지지 마세요. 실패는 상태에 담아야 루프를 돌릴 수 있습니다.
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from src.agent.prompts import answer_prompt, fix_prompt, sql_prompt
from src.agent.state import AgentState
from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def get_llm() -> ChatOpenAI:
    """Groq 등 OpenAI 호환 엔드포인트. base_url 만 바꾸면 제공자를 갈아끼울 수 있습니다."""
    return ChatOpenAI(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        temperature=0,
    )


def retrieve_node(state: AgentState) -> dict:
    """온톨로지 검색 -> 컨텍스트 + 조인 SQL 생성.

    TODO 1:
      result = search(state["question"])
      if result.blocked_reason:
          return {"blocked_reason": result.blocked_reason}

      onto = load_ontology()
      entity_names = [e.name for e in result.entities]
      return {
          "entities": entity_names,
          "metrics": [m.name for m in result.metrics],
          "context": render_context(onto, result.entities, result.metrics, result.terms),
          "join_sql": build_join_sql(onto, entity_names),
          "blocked_reason": None,
      }

    성능 힌트: load_ontology() 를 노드마다 호출하면 매번 YAML 을 다시 읽습니다.
             모듈 수준에서 한 번만 로드하거나 functools.lru_cache 를 씌우세요.
    """
    raise NotImplementedError  # TODO


def generate_node(state: AgentState) -> dict:
    """SQL 생성 (최초) 또는 수리 (재시도).

    TODO 2: 프로젝트 1의 generate_node 와 같은 구조입니다.
            state["error"] 유무로 sql_prompt / fix_prompt 를 가릅니다.
            attempts 를 반드시 1 증가시키세요. 안 하면 무한 루프입니다.
    """
    raise NotImplementedError  # TODO


def execute_node(state: AgentState) -> dict:
    """SQL 실행. 실패는 예외가 아니라 상태로 돌려준다.

    TODO 3:
      try:
          return {"df": run_sql(state["sql"]), "error": None}
      except Exception as e:
          return {"df": None, "error": f"{type(e).__name__}: {e}"}
    """
    raise NotImplementedError  # TODO


def answer_node(state: AgentState) -> dict:
    """최종 답변 생성.

    TODO 4: 세 갈래를 모두 처리하세요.
      1) blocked_reason 이 있으면 -> "이 데이터에는 없는 정보입니다" + 이유
      2) error 가 남아 있으면    -> 실패 사실 + 마지막 SQL/오류
      3) 정상                    -> answer_prompt 로 자연어 답변

    1번을 빼먹기 쉬운데, 이게 없으면 차단해놓고 빈 답을 내보내게 됩니다.
    """
    raise NotImplementedError  # TODO


# ─────────────────────────────────────────────────────────────
# 라우팅 함수
# ─────────────────────────────────────────────────────────────
MAX_ATTEMPTS = 3


def route_after_retrieve(state: AgentState) -> str:
    """TODO 5: blocked_reason 이 있으면 "blocked", 없으면 "generate" 를 반환."""
    raise NotImplementedError


def route_after_execute(state: AgentState) -> str:
    """TODO 6: 에러가 있고 attempts < MAX_ATTEMPTS 면 "retry", 아니면 "answer"."""
    raise NotImplementedError
