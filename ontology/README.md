# 온톨로지 작성 가이드

## 온톨로지가 뭘 하는가

dbt가 만든 마트 테이블은 **물리 구조**입니다. `fct_sales.line_amount` 라는 컬럼이 있다는 사실만 알려주죠.
온톨로지는 그 위에 **의미**를 얹습니다.

```
물리:  analytics_marts.fct_sales.line_amount  (numeric)
의미:  "매출" = SUM(line_amount),  동의어: 매출액, 판매금액, 총매출, revenue
       측정 가능한 축: 국가, 장르, 월, 담당자
```

이 매핑이 있으면 사용자가 `"작년 국가별 매출"` 이라고 말했을 때
LLM이 `line_amount` 라는 컬럼을 **추측할 필요가 없어집니다.**

## 파일 4개의 역할

| 파일 | 답하는 질문 | 예 |
|---|---|---|
| `entities.yml` | 이 세계에 **무엇이 있나** | 고객, 곡, 판매, 직원 |
| `relationships.yml` | 그것들이 **어떻게 이어지나** | 판매 → 고객 (다대일) |
| `metrics.yml` | **무엇을 셀 수 있나** | 총매출, 주문수, 객단가 |
| `glossary.yml` | 업무 **용어의 정의** | "활성 고객" = 최근 12개월 구매자 |

## 작성 원칙

**1. 사용자의 말로 쓰세요.** 컬럼명이 아니라 사람들이 실제로 쓰는 단어입니다.
`synonyms` 가 검색 정확도를 좌우합니다. 아깝다 생각 말고 많이 넣으세요.

**2. 지표는 반드시 하나로만 정의하세요.**
"매출"이 두 곳에 다르게 정의돼 있으면 온톨로지를 쓰는 의미가 없습니다.
`metrics.yml` 이 유일한 진실의 원천(single source of truth)입니다.

**3. 관계는 방향과 카디널리티를 명시하세요.**
LLM이 조인을 만들지 않게 하는 것이 목적입니다. 여기 적힌 대로만 조인하게 됩니다.

**4. 없는 건 없다고 쓰세요.**
`glossary.yml` 에 "이 DB에는 없는 정보" 항목을 두면 환각을 크게 줄일 수 있습니다.
(예: 연봉, 재고, 원가 — Chinook 에는 없습니다)

## 작성 순서 추천

1. `entities.yml` 에 마트 테이블 4개를 그대로 엔티티로 등록
2. `relationships.yml` 에 fct_sales 를 중심으로 한 조인 경로
3. `metrics.yml` 에 자주 물어볼 지표 5개
4. 평가 질문(`evals/questions.yml`)을 써 보고, 답하는 데 필요한 게 빠졌으면 되돌아와 추가

## 검증

```powershell
..\.venv\Scripts\python.exe -m src.ontology.loader
```

`loader.py` 가 YAML을 읽어 `src/ontology/models.py` 의 dataclass 로 변환합니다.
**dataclass 정의가 곧 YAML 스키마 계약서**이니, 어떤 필드를 써야 할지 헷갈리면 그 파일을 보세요.
