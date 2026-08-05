from __future__ import annotations

from pathlib import Path

import yaml

from src.config import ONTOLOGY_DIR
from src.ontology.models import (
    Attribute,
    Entity,
    Metric,
    NotCovered,
    Ontology,
    Relationship,
    Term,
)


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ─────────────────────────────────────────────────────────────
# TODO 1: 엔티티 파싱
#
    # raw = _read_yaml(ONTOLOGY_DIR / "entities.yml")
    # print(raw)
    # for item in raw.get("entities", []):
    #     attributes = [Attribute(**a) for a in item.pop("attributes", [])]
    #     entities.append(Entity(**item, attributes=attributes))
#
#   힌트: Attribute(**a) 는 YAML 키와 dataclass 필드 이름이 정확히 같아야 동작합니다.
#        오타가 있으면 TypeError 가 나는데, 그게 바로 우리가 원하는 조기 실패입니다.
# ─────────────────────────────────────────────────────────────
def load_entities() -> list[Entity]:
    raw = _read_yaml(ONTOLOGY_DIR / "entities.yml")
    entities = []

    for item in raw.get("entities", []):
        attributes = [Attribute(**a) for a in item.pop("attributes", [])]
        entities.append(Entity(**item, attributes=attributes))

    return entities

# ─────────────────────────────────────────────────────────────
# TODO 2: 관계 파싱
#
#   주의: YAML 키는 from / to 이지만 dataclass 필드는 from_entity / to_entity 입니다.
#         (from 은 파이썬 예약어라 필드명으로 못 씁니다)
#
#   item["from_entity"] = item.pop("from")
#   item["to_entity"] = item.pop("to")
# ─────────────────────────────────────────────────────────────
def load_relationships() -> list[Relationship]:
    raw = _read_yaml(ONTOLOGY_DIR / "relationships.yml")
    relationshop = []

    for item in raw.get("relationships", []):
        item["from_entity"] = item.pop("from")
        item["to_entity"] = item.pop("to")
        relationshop.append(Relationship(**item))

    # print(relationshop)
    return relationshop


def load_metrics() -> list[Metric]:
    raw = _read_yaml(ONTOLOGY_DIR / "metrics.yml")
    metric = []
    for item in raw.get("metrics", []):
        metric.append(Metric(**item))

    return metric


def load_glossary() -> tuple[list[Term], list[NotCovered]]:
    """glossary.yml 은 terms 와 not_covered 두 섹션을 갖습니다."""
    raw = _read_yaml(ONTOLOGY_DIR / "glossary.yml")
    terms = []
    not_cover = []

    for item in raw.get("terms", []):
        terms.append(Term(**item))

    for item in raw.get("not_covered", []):
        not_cover.append(NotCovered(**item))

    return terms, not_cover
        


def load_ontology() -> Ontology:
    terms, not_covered = load_glossary()
    return Ontology(
        entities=load_entities(),
        relationships=load_relationships(),
        metrics=load_metrics(),
        terms=terms,
        not_covered=not_covered,
    )


def validate(onto: Ontology) -> list[str]:
    """온톨로지 무결성 검사. 반환값은 문제 목록(비어 있으면 정상).

    TODO 5: 아래 항목을 검사하세요. 이 검증이 나중에 디버깅 시간을 크게 줄여줍니다.

      - 모든 relationship 의 from/to 가 실제 존재하는 엔티티인가
      - 모든 metric 의 entity 가 존재하는가
      - metric.dimensions 의 "entity.attribute" 가 실제로 존재하는가
      - 엔티티 이름 중복은 없는가
      - (선택) src.db.list_mart_tables() 와 비교해 실제 테이블이 있는가
        -> 온톨로지와 dbt 모델이 어긋나는 것을 잡아줍니다. 가장 흔한 버그입니다.
    """
    problems: list[str] = []
    # TODO
    return problems


if __name__ == "__main__":
    onto = load_ontology()
    print(f"엔티티   {len(onto.entities)}개: {[e.name for e in onto.entities]}")
    print(f"관계     {len(onto.relationships)}개")
    print(f"지표     {len(onto.metrics)}개: {[m.name for m in onto.metrics]}")
    print(f"용어     {len(onto.terms)}개")
    print(f"미보유   {len(onto.not_covered)}개")

    issues = validate(onto)
    if issues:
        print("\n[검증 실패]")
        for issue in issues:
            print("  -", issue)
    else:
        print("\n검증 통과")
  