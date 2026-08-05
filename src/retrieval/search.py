"""질문 -> 필요한 온톨로지 조각.

프로젝트 1의 retrieve_schema() 에 해당하지만, 두 가지가 달라집니다.
    1. 종류별로 따로 검색한다 (엔티티 / 지표 / 용어 / 미보유)
    2. 관계 확장이 '외래키 추론'이 아니라 '온톨로지 조회'다
"""

from __future__ import annotations

from dataclasses import dataclass

from src.ontology.loader import load_ontology
from src.ontology.models import Entity, Metric, Ontology, Term
from src.retrieval.index import get_vectorstore


@dataclass
class RetrievalResult:
    entities: list[Entity]
    metrics: list[Metric]
    terms: list[Term]
    blocked_reason: str = ""     # not_covered 에 걸리면 이유가 채워진다


def search(question: str, k_entity: int = 3, k_metric: int = 3) -> RetrievalResult:
    """질문에 필요한 온톨로지 조각을 모은다.

    TODO 1: 종류별 검색
        vs = get_vectorstore()
        ent_hits = vs.similarity_search(question, k=k_entity, filter={"kind": "entity"})
        met_hits = vs.similarity_search(question, k=k_metric, filter={"kind": "metric"})
        ...
        Chroma 의 filter 는 metadata 를 대상으로 합니다. index.py 에서 kind 를 넣어둔 이유죠.

    TODO 2: 미보유 주제 차단
        not_covered 문서를 점수와 함께 검색해서(similarity_search_with_score),
        거리가 임계값보다 가까우면 blocked_reason 을 채우고 즉시 반환하세요.
        임계값은 직접 실험해서 정해야 합니다. bge-m3 기준 대략 0.9~1.1 근처부터 시작해
        "연봉 얼마야?"는 걸리고 "매출 얼마야?"는 안 걸리는 값을 찾으세요.

        **이 임계값 튜닝이 이 프로젝트에서 가장 실무적인 작업입니다.**
        너무 낮으면 환각을 못 막고, 너무 높으면 정상 질문을 거절합니다.

    TODO 3: 지표로부터 엔티티 확장
        지표가 검색되면 그 지표의 entity 와 dimensions 에 등장하는 엔티티를
        자동으로 추가하세요.
          total_revenue 가 잡혔는데 sales 엔티티가 안 잡히면 SQL 을 못 만듭니다.
        프로젝트 1의 '다리 테이블 자동 추가'와 같은 발상입니다.
        다만 이번엔 추론이 아니라 온톨로지에 적힌 사실을 읽는 것뿐입니다.
    """
    raise NotImplementedError


if __name__ == "__main__":
    for q in [
        "작년 국가별 매출 알려줘",
        "락 장르에서 가장 많이 팔린 곡은?",
        "직원들 연봉이 얼마야?",
    ]:
        result = search(q)
        print(f"\nQ: {q}")
        if result.blocked_reason:
            print(f"  차단됨: {result.blocked_reason}")
            continue
        print(f"  엔티티: {[e.name for e in result.entities]}")
        print(f"  지표:   {[m.name for m in result.metrics]}")
        print(f"  용어:   {[t.term for t in result.terms]}")
