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


def load_entities() -> list[Entity]:
    """  힌트: Attribute(**a) 는 YAML 키와 dataclass 필드 이름이 정확히 같아야 동작합니다.
        오타가 있으면 TypeError 가 나는데, 눈에 보이게하는 실패입니다."""
    raw = _read_yaml(ONTOLOGY_DIR / "entities.yml")
    entities = []

    for item in raw.get("entities", []):
        attributes = [Attribute(**a) for a in item.pop("attributes", [])]
        entities.append(Entity(**item, attributes=attributes))

    return entities


def load_relationships() -> list[Relationship]:
    raw = _read_yaml(ONTOLOGY_DIR / "relationships.yml")
    relationshop = []

    for item in raw.get("relationships", []):
        item["from_entity"] = item.pop("from")
        item["to_entity"] = item.pop("to")
        relationshop.append(Relationship(**item))

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
    from collections import Counter
    problems: list[str] = []

    # 조회용 자료 구조 만들기
    entity_names = [e.name for e in onto.entities]
    by_name = {e.name : e for e in onto.entities }
    # 엔티티별 속성 집합 (dict 중첩 ) - list 루프 안씀 
    atts_of = {e.name: {a.name for a in e.attributes} for e in onto.entities}
    
    for k, v in Counter(entity_names).items():
        if v > 1:
            problems.append(f"Entity {k}가 {v}번 중복됩니다.")

    for r in onto.relationships:
        if r.from_entity not in by_name:
            problems.append(f"Relationship '{r.name}': from '{r.from_entity}'가 존재하지 않습니다.")
        if r.to_entity not in by_name:
            problems.append(f"Relationship '{r.name}': to '{r.to_entity}'가 존재하지 않습니다.")

    # Metric 안에 Fct Entity 탐색
    for m in onto.metrics:
        if m.entity not in by_name:
            problems.append(f"Metric {m.name}에 {m.entity}가 존재하지 않습니다.")

    # Metric 안에 dimensions 탐색(어렵다)
    for m in onto.metrics:
        for dim in m.dimensions:
            # 1) 형식 검사
            parts = dim.split(".")
            if len(parts) !=2:
                problems.append(f"Metric {m.name}에 entity.attribute 형식이 아닙니다. {dim}")
                continue

            ent_name, attr_name = parts

            # 2) dim 엔티티 존재 검사
            if ent_name not in atts_of:
                problems.append(f"Metric {m.name}에 {ent_name}이 없습니다.")
                continue

            # 3) 속성 존재 검사
            if attr_name not in atts_of[ent_name]:
                problems.append(f"Metric {m.name}에 {ent_name}에 {attr_name}이 속성이 없습니다.")

    # 실제 테이블이 존재하는지 확인
    from src.db import list_mart_tables

    entities = list_mart_tables()
    check = [ent for ent in entities if ent not in by_name]
    for item in check:
        problems.append(f"테이블 {item}이 실제 DB에 존재하지 않습니다.")

    
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
  