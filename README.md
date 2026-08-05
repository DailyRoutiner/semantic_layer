# 온톨로지 기반 Text-to-SQL

dbt 시맨틱 레이어 위에 **커스텀 YAML 온톨로지**를 얹고, LangGraph 에이전트가 그 온톨로지를 근거로 SQL을 생성하는 프로젝트입니다.

> 이 저장소는 **스켈레톤**입니다. `TODO`가 달린 곳을 직접 채우면서 완성하세요.
> 각 파일 상단에 "무엇을 / 왜 / 힌트"가 주석으로 적혀 있습니다.

---

## 1. 왜 온톨로지인가

앞선 프로젝트(`rag_with_langgraph_01.ipynb`)에서는 **원본 테이블 스키마**를 벡터 검색해서 LLM에 넣었습니다. 한계가 명확했죠.

| 문제 | 원본 스키마 RAG | 온톨로지 + 시맨틱 레이어 |
|---|---|---|
| `InvoiceLine` 같은 무의미한 이름 | 임베딩이 못 찾음 | `판매` 라는 **비즈니스 이름**으로 검색 |
| JOIN 경로 | LLM이 추론 (틀릴 수 있음) | 온톨로지가 **경로를 알려줌** |
| "매출"의 정의 | 매번 LLM이 새로 해석 | `metrics.yml`에 **한 번만** 정의 |
| 정규화된 5개 테이블 JOIN | 매번 LLM이 조립 | dbt가 **미리 조립해 둠** (`fct_sales`) |
| 같은 질문 → 다른 SQL | 자주 발생 | 정의가 고정돼 재현성 확보 |

핵심 아이디어는 **LLM에게 자유를 덜 주는 것**입니다. 물리 스키마를 통째로 던지고 알아서 하라는 대신, 비즈니스 개념(엔티티·지표·관계)만 보여주고 그 안에서 조합하게 합니다.

```
    사용자 질문 ("작년 국가별 매출 알려줘")
          |
    [온톨로지 검색]  entity: 고객·판매 / metric: 총매출 / dimension: 국가
          |
    [JOIN 경로 계산]  relationships.yml 이 fct_sales -> dim_customer 경로를 제공
          |
    [SQL 생성]  LLM은 "무엇을 고를지"만 결정. 테이블/조인/지표식은 온톨로지가 제공
          |
    [실행]  dbt가 만든 마트 테이블에 대해서만 실행 (읽기 전용)
```

---

## 2. 아키텍처

```
Chinook.db (SQLite)
      |  scripts/load_chinook.py
      v
PostgreSQL  raw 스키마          <- 원본 적재
      |  dbt run
      v
PostgreSQL  analytics 스키마     <- staging(view) + marts(table)
      |                             dim_customer, dim_track, dim_employee, fct_sales
      |
ontology/*.yml                   <- 사람이 쓰는 비즈니스 정의 (마트 컬럼에 매핑)
      |  src/ontology/compiler.py
      v
검색 문서 + JOIN 경로 + 프롬프트 컨텍스트
      |  src/retrieval, src/agent
      v
LangGraph 에이전트 -> SQL -> 실행 -> 답변
```

**계층 3개의 역할 분담**을 기억하세요.

| 계층 | 담당 | 도구 |
|---|---|---|
| 물리 | 데이터를 어떻게 저장/변환할까 | dbt (SQL) |
| 의미 | 이 컬럼이 비즈니스적으로 무엇인가 | ontology YAML |
| 대화 | 사용자 말을 의미 계층에 어떻게 매핑할까 | LangGraph + LLM |

---

## 3. 단계별 체크리스트

순서대로 진행하세요. 각 단계 끝에 **확인 명령**이 있습니다.

### 0단계 — 환경 준비

```powershell
# 프로젝트 루트의 기존 venv 재사용
..\.venv\Scripts\pip.exe install -r requirements.txt

copy .env.example .env
# .env 를 열어 GROQ_API_KEY 등을 채우세요
```

- [ ] Docker Desktop 실행
- [ ] `docker compose up -d` 로 Postgres 기동
- [ ] `docker compose ps` 에서 healthy 확인

> **Python 3.13에서 `dbt-core` 설치가 실패하면** `requirements.txt`의 dbt 두 줄을 지우고,
> 전역에 이미 설치된 `dbt-fusion`(`C:\Users\<you>\.local\bin\dbt.exe`)을 쓰거나
> Python 3.12로 별도 venv를 만드세요.

### 1단계 — 원본 적재

```powershell
..\.venv\Scripts\python.exe scripts\load_chinook.py
```

- [ ] `raw` 스키마에 11개 테이블 생성 확인
- [ ] 컬럼명이 `snake_case`로 변환됐는지 확인 (`InvoiceLineId` -> `invoice_line_id`)

### 2단계 — dbt staging 모델

`dbt/models/staging/` 에서 작업합니다.

- [ ] `_sources.yml` — 11개 원본 테이블 등록 (TODO)
- [ ] `stg_customers.sql` — **완성 예시 제공됨.** 읽고 패턴을 익히세요
- [ ] `stg_invoices.sql`, `stg_invoice_lines.sql`, `stg_tracks.sql`, `stg_genres.sql`, `stg_employees.sql`, `stg_albums.sql`, `stg_artists.sql` (TODO)

```powershell
cd dbt
..\..\.venv\Scripts\dbt.exe run --select staging
..\..\.venv\Scripts\dbt.exe test
```

### 3단계 — dbt 마트 (스타 스키마)

`dbt/models/marts/` 에서 작업합니다. **이 프로젝트의 핵심 산출물**입니다.

- [ ] `dim_customer.sql` — 완성 예시 제공됨
- [ ] `dim_track.sql` — 곡 + 장르 + 앨범 + 아티스트를 **미리 조인**해 둡니다 (TODO)
- [ ] `dim_employee.sql` (TODO)
- [ ] `fct_sales.sql` — 판매 1행 = `invoice_line` 1행. 날짜·고객·직원 키를 다 붙입니다 (TODO)
- [ ] `_marts.yml` — 테스트(`unique`, `not_null`, `relationships`)와 설명 (TODO)

```powershell
..\..\.venv\Scripts\dbt.exe run
..\..\.venv\Scripts\dbt.exe test
```

> **왜 미리 조인해 두나** — 프로젝트 1에서 LLM이 `InvoiceLine -> Track -> Genre` 3중 조인을 매번 짜야 했습니다.
> `dim_track`에 `genre_name`을 미리 넣어두면 LLM은 조인을 아예 생각할 필요가 없습니다.
> **LLM이 할 일을 줄이는 게 정확도를 올리는 가장 확실한 방법입니다.**

### 4단계 — 온톨로지 작성

`ontology/` 에서 작업합니다. 자세한 가이드는 [ontology/README.md](ontology/README.md).

- [ ] `entities.yml` — `customer` 완성 예시 있음. `sales`, `track`, `employee` 추가 (TODO)
- [ ] `relationships.yml` — 마트 간 JOIN 경로 (TODO)
- [ ] `metrics.yml` — `total_revenue` 예시 있음. 지표 3~5개 추가 (TODO)
- [ ] `glossary.yml` — "활성 고객" 같은 업무 용어 (TODO)

```powershell
..\.venv\Scripts\python.exe -m src.ontology.loader   # 검증 실행
```

### 5단계 — 검색 인덱스

- [ ] `src/ontology/compiler.py` — 온톨로지를 검색 문서로 변환 (TODO)
- [ ] `src/retrieval/index.py` — Chroma 인덱싱 (TODO)
- [ ] `src/retrieval/search.py` — 검색 + 관계 확장 (TODO)

### 6단계 — LangGraph 에이전트

- [ ] `src/agent/state.py` (TODO)
- [ ] `src/agent/prompts.py` (TODO)
- [ ] `src/agent/nodes.py` (TODO)
- [ ] `src/agent/graph.py` (TODO)

### 7단계 — 평가

- [ ] `evals/questions.yml` 채우기
- [ ] 정답률 측정 후 프롬프트/온톨로지 개선

---

## 4. 디렉터리 안내

```
ontology_text2sql/
├── docker-compose.yml      Postgres 16
├── requirements.txt
├── .env.example
├── scripts/
│   └── load_chinook.py     SQLite -> Postgres 적재 (완성)
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/        원본 정리 (view)
│       └── marts/          스타 스키마 (table)
├── ontology/               비즈니스 의미 정의 (YAML)
├── src/
│   ├── config.py           환경 설정 (완성)
│   ├── db.py               읽기 전용 DB 접속 (TODO)
│   ├── ontology/
│   │   ├── models.py       dataclass 정의 (완성 - 이게 YAML의 계약서입니다)
│   │   ├── loader.py       YAML -> dataclass (TODO)
│   │   └── compiler.py     온톨로지 -> 문서/JOIN/프롬프트 (TODO)
│   ├── retrieval/          벡터 검색 (TODO)
│   └── agent/              LangGraph (TODO)
├── evals/questions.yml     평가셋
└── notebooks/
    └── 01_walkthrough.ipynb  단계별 실습
```

---

## 5. 막혔을 때

- 각 TODO 주석에 **힌트**와 **참고할 파일**이 적혀 있습니다
- 완성 예시가 있는 파일: `stg_customers.sql`, `dim_customer.sql`, `entities.yml`의 `customer`, `metrics.yml`의 `total_revenue`, `src/ontology/models.py`
- dbt 문법이 막히면 `dbt compile` 로 생성되는 SQL을 `dbt/target/compiled/` 에서 확인하세요
