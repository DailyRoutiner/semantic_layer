"""온톨로지 -> (검색 문서 / JOIN SQL / 프롬프트 컨텍스트).

**이 파일이 프로젝트의 두뇌입니다.** 온톨로지는 데이터일 뿐이고,
그걸 LLM이 쓸 수 있는 형태로 바꾸는 게 여기입니다.

만들 것 3가지:
    1. to_documents()      온톨로지 -> 벡터 검색용 문서들
    2. build_join_sql()    선택된 엔티티들 -> FROM/JOIN 절
    3. render_context()    선택된 것들 -> 프롬프트에 넣을 텍스트
"""

from __future__ import annotations

from src.ontology.models import Entity, Metric, Ontology


# ─────────────────────────────────────────────────────────────
# 1. 검색 문서 만들기
# ─────────────────────────────────────────────────────────────
def to_documents(onto: Ontology) -> list[dict]:
    """온톨로지를 검색 문서 리스트로 변환.

    반환 형식: [{"id": ..., "kind": ..., "name": ..., "text": ...}, ...]
      kind 는 entity | metric | term | not_covered 중 하나.

    **문서 종류를 나누는 게 핵심입니다.** 프로젝트 1은 테이블 문서 한 종류였지만,
    여기서는 지표와 용어도 각각 독립적으로 검색돼야 합니다.
    "매출"이라고 물으면 metric 문서가, "활성 고객"이라 물으면 term 문서가 잡혀야 하니까요.

    TODO 1: 엔티티 문서
        text 에 넣을 것 — label, description, synonyms, grain,
                        각 attribute 의 label/synonyms/sample_values
        힌트: 컬럼명(customer_country)보다 label(국가)과 synonyms 가 검색을 좌우합니다.
             프로젝트 1에서 '설명을 넣으니 InvoiceLine 이 잡혔던' 그 원리입니다.

    TODO 2: 지표 문서
        text 에 넣을 것 — label, description, synonyms, 사용 가능한 dimensions
        expression 은 넣지 마세요. SQL 조각은 검색에 도움이 안 되고 노이즈만 늘립니다.
        (검색된 뒤 render_context 에서 붙이면 됩니다)

    TODO 3: 용어 문서, not_covered 문서
        not_covered 는 특히 중요합니다. "연봉" 질문이 이 문서를 잡으면
        SQL 생성 없이 바로 거절할 수 있습니다.
    """
    raise NotImplementedError  # TODO


# ─────────────────────────────────────────────────────────────
# 2. JOIN SQL 만들기  <- 온톨로지를 쓰는 가장 큰 이유
# ─────────────────────────────────────────────────────────────
def build_join_sql(onto: Ontology, entity_names: list[str], base: str = "sales") -> str:
    """선택된 엔티티들을 잇는 FROM ... JOIN ... 절을 문자열로 만든다.

    예상 출력:
        FROM analytics_marts.fct_sales
        LEFT JOIN analytics_marts.dim_customer
               ON fct_sales.customer_id = dim_customer.customer_id
        LEFT JOIN analytics_marts.dim_track
               ON fct_sales.track_id = dim_track.track_id

    **LLM 은 이 문자열을 그대로 받아씁니다.** 조인을 생각할 필요가 없어집니다.
    프로젝트 1에서 외래키 그래프로 '다리 테이블'을 찾던 것의 상위 호환입니다.

    TODO 4:
      - base 엔티티(보통 팩트 = sales)를 FROM 에 둔다
      - 나머지 엔티티마다 relationships 에서 base 와 잇는 관계를 찾아 JOIN 을 만든다
      - 관계가 없으면 예외를 던지거나 문제 목록에 담는다.
        **조용히 빠뜨리면 LLM 이 데카르트 곱을 만듭니다.** 반드시 시끄럽게 실패하세요.

    한 단계 더 (선택):
      base 와 직접 연결되지 않은 엔티티는 관계 그래프에서 최단 경로를 찾아
      중간 엔티티까지 함께 조인해야 합니다. BFS 로 구현해 보세요.
      스타 스키마라 지금은 대부분 1홉이지만, 실무 스키마에선 필수입니다.
    """
    raise NotImplementedError  # TODO


# ─────────────────────────────────────────────────────────────
# 3. 프롬프트 컨텍스트 만들기
# ─────────────────────────────────────────────────────────────
def render_context(
    onto: Ontology,
    entities: list[Entity],
    metrics: list[Metric],
    terms: list = None,
) -> str:
    """검색된 온톨로지 조각들을 프롬프트에 넣을 텍스트로 조립한다.

    TODO 5: 아래 구조로 만드세요.

        ## 사용 가능한 테이블
        analytics_marts.fct_sales  (판매. 한 행 = 주문 상세 1줄)
          - line_amount   금액 (numeric)
          - quantity      수량
          ...

        ## 조인 방법 (아래 그대로 사용할 것)
        FROM ... LEFT JOIN ...

        ## 지표 정의 (반드시 이 식을 사용할 것)
        총매출 = SUM(fct_sales.line_amount)
          주의: invoice_total 과 혼동 금지

        ## 용어 정의
        활성 고객 = ...

    프롬프트 작성 요령:
      - "반드시", "그대로", "지어내지 말 것" 같은 강한 표현을 쓰세요
      - 지표 expression 은 **복사해서 쓰라고** 명시하세요.
        LLM 이 SUM(line_amount) 를 AVG 로 바꾸는 일이 실제로 일어납니다
      - 검색되지 않은 테이블/컬럼은 아예 보여주지 마세요.
        보이면 씁니다. 안 보이면 못 씁니다.
    """
    raise NotImplementedError  # TODO
