"""온톨로지 YAML 의 계약서(스키마).

✅ 완성본입니다. **YAML 을 쓰다가 어떤 필드가 있는지 헷갈리면 이 파일을 보세요.**

왜 dataclass 로 감싸나:
    YAML 을 dict 로 그냥 쓰면 오타(`synonym` vs `synonyms`)를 실행 시점까지 모릅니다.
    dataclass 로 변환하면 로딩 순간에 터지므로 문제를 빨리 발견합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Attribute:
    """엔티티가 가진 속성 = 마트 테이블의 컬럼 하나."""

    name: str                                   # 실제 컬럼명
    label: str = ""                             # 사람이 읽는 이름
    type: str = "text"                          # id | text | category | number | date
    synonyms: list[str] = field(default_factory=list)
    sample_values: list[str] = field(default_factory=list)
    note: str = ""                              # 주의사항. 프롬프트에 그대로 들어간다


@dataclass
class Entity:
    """엔티티 = 마트 테이블 하나에 대응하는 비즈니스 개념."""

    name: str                                   # 온톨로지 내부 식별자 (customer, sales...)
    label: str = ""
    description: str = ""
    synonyms: list[str] = field(default_factory=list)
    model: str = ""                             # dbt 모델명 = 테이블명
    schema: str = ""                            # Postgres 스키마
    primary_key: str = ""
    grain: str = ""                             # "한 행 = 무엇인가"
    attributes: list[Attribute] = field(default_factory=list)

    @property
    def table(self) -> str:
        """프롬프트/SQL 에 쓸 정규화된 테이블 이름."""
        return f"{self.schema}.{self.model}" if self.schema else self.model


@dataclass
class Relationship:
    """엔티티 간 조인 경로.

    주의: YAML 의 키는 `from` 이지만 파이썬 예약어라 여기서는 from_entity 입니다.
          loader 에서 매핑해 주세요.
    """

    name: str
    from_entity: str
    to_entity: str
    from_key: str
    to_key: str
    cardinality: str = "many_to_one"            # many_to_one | one_to_many | one_to_one
    join_type: str = "left"                     # left | inner
    description: str = ""


@dataclass
class Metric:
    """집계 정의. 이 프로젝트에서 가장 값진 자산."""

    name: str
    label: str = ""
    description: str = ""
    synonyms: list[str] = field(default_factory=list)
    entity: str = ""                            # 어느 엔티티 기준으로 계산하나
    expression: str = ""                        # SQL 집계식 (그대로 사용됨)
    format: str = "number"                      # number | currency | percent
    dimensions: list[str] = field(default_factory=list)   # "entity.attribute" 형식
    note: str = ""


@dataclass
class Term:
    """업무 용어 정의."""

    term: str
    definition: str = ""
    synonyms: list[str] = field(default_factory=list)
    sql_hint: str = ""
    note: str = ""


@dataclass
class NotCovered:
    """이 DB 에 없는 정보. 환각 방지용."""

    topic: str
    reason: str = ""
    synonyms: list[str] = field(default_factory=list)


@dataclass
class Ontology:
    """온톨로지 전체."""

    entities: list[Entity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    terms: list[Term] = field(default_factory=list)
    not_covered: list[NotCovered] = field(default_factory=list)

    def entity(self, name: str) -> Entity | None:
        return next((e for e in self.entities if e.name == name), None)

    def metric(self, name: str) -> Metric | None:
        return next((m for m in self.metrics if m.name == name), None)
