# SETUP — 환경 구축 & 단계별 실습 가이드

프로젝트 개요와 설계 배경은 [README.md](README.md)를 먼저 읽으세요.
이 문서는 **직접 굴려보기 위한 절차**만 담습니다.

> 이 저장소는 학습용 **스켈레톤**입니다. `TODO`가 달린 곳을 직접 채우면서 완성합니다.
> 각 파일 상단에 "무엇을 / 왜 / 힌트"가 주석으로 적혀 있습니다.

> **로컬 전용 파일**: `docker-compose.yml`, `scripts/`, `notebooks/`, `.env*` 는 `.gitignore`에 걸려 있어
> 저장소에 커밋되지 않습니다. 새 환경에서 시작한다면 아래 0~1단계에서 직접 만들어야 합니다.

---

## 0단계 — 환경 준비

```powershell
# 프로젝트 루트의 기존 venv 재사용
..\.venv\Scripts\pip.exe install -r requirements.txt

copy .env.example .env
# .env 를 열어 GROQ_API_KEY 등을 채우세요
```

- [ ] Docker Desktop 실행
- [ ] `docker compose up -d` 로 Postgres 16 기동
- [ ] `docker compose ps` 에서 healthy 확인

`docker-compose.yml`은 `.env`와 값이 일치해야 합니다 (`PGUSER=dbt`, `PGPASSWORD=dbt_password`, `PGDATABASE=analytics`).

> **Python 3.13에서 `dbt-core` 설치가 실패하면** `requirements.txt`의 dbt 두 줄을 지우고
> Python 3.12로 별도 venv를 만드세요.
> 전역에 설치된 `dbt-fusion`(`C:\Users\<you>\.local\bin\dbt.exe`)은 이 프로젝트와 호환되지 않으므로
> **반드시 venv 안의 `dbt.exe`를 경로로 지정해 실행**합니다.

### 읽기 전용 계정 만들기

에이전트가 쓸 계정입니다. 마트 스키마만 SELECT 가능하게 하고 raw/staging에는 권한을 주지 않습니다.

```powershell
docker compose exec postgres psql -U dbt -d analytics
```

```sql
CREATE USER rag_reader WITH PASSWORD 'rag_reader_password';
GRANT USAGE ON SCHEMA analytics_marts TO rag_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics_marts TO rag_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics_marts
  GRANT SELECT ON TABLES TO rag_reader;
```

---

## 1단계 — 원본 적재

```powershell
..\.venv\Scripts\python.exe scripts\load_chinook.py
```

- [ ] `raw` 스키마에 11개 테이블 생성 확인
- [ ] 컬럼명이 `snake_case`로 변환됐는지 확인 (`InvoiceLineId` → `invoice_line_id`)

---

## 2단계 — dbt staging 모델

`dbt/models/staging/` 에서 작업합니다. 원본을 정리만 하므로 `view`로 만듭니다.

- [x] `_sources.yml` — 11개 원본 테이블 등록
- [x] `stg_customers.sql` — 완성 예시. 읽고 패턴을 익히세요
- [x] `stg_invoices.sql`, `stg_invoice_lines.sql`, `stg_tracks.sql`, `stg_genres.sql`, `stg_employees.sql`, `stg_albums.sql`, `stg_artists.sql`

```powershell
cd dbt
..\..\.venv\Scripts\dbt.exe run --select staging --profiles-dir .
..\..\.venv\Scripts\dbt.exe test --profiles-dir .
```

---

## 3단계 — dbt 마트 (스타 스키마)

`dbt/models/marts/` 에서 작업합니다. **이 프로젝트의 핵심 산출물**입니다.

- [x] `dim_customer.sql`
- [x] `dim_track.sql` — 곡 + 장르 + 앨범 + 아티스트를 **미리 조인**
- [x] `dim_employee.sql`
- [x] `fct_sales.sql` — 한 행 = `invoice_line` 1행. 날짜·고객·직원 키를 다 붙임
- [x] `_marts.yml` — `unique`, `not_null`, `relationships` 테스트와 설명

```powershell
..\..\.venv\Scripts\dbt.exe run --profiles-dir .
..\..\.venv\Scripts\dbt.exe test --profiles-dir .
```

> **왜 미리 조인해 두나** — 선행 프로젝트에서 LLM이 `InvoiceLine → Track → Genre` 3중 조인을 매번 짜야 했습니다.
> `dim_track`에 `genre_name`을 미리 넣어두면 LLM은 조인을 아예 생각할 필요가 없습니다.
> **LLM이 할 일을 줄이는 게 정확도를 올리는 가장 확실한 방법입니다.**

> **팩트 테이블 규칙** — 차원의 '이름'(track_name, customer_name)은 팩트에 넣지 않습니다.
> 팩트에는 키와 숫자만 둡니다. 이 규칙을 지켜야 스타 스키마가 유지됩니다.

---

## 4단계 — 온톨로지 작성

`ontology/` 에서 작업합니다. 자세한 가이드는 [ontology/README.md](ontology/README.md).

- [x] `entities.yml` — `customer`, `sales`, `track`, `employee`
- [x] `relationships.yml` — `sales_to_customer`, `sales_to_track`, `sales_to_employee`
- [x] `metrics.yml` — `total_revenue`, `order_count`, `units_sold`
  - [ ] `avg_order_value` — `SUM(line_amount) / NULLIF(COUNT(DISTINCT invoice_id), 0)`
  - [ ] `customer_count` — `COUNT(DISTINCT customer_id)`. note에 "전체 고객수가 아니라 구매 이력이 있는 고객수"라고 명시
- [x] `glossary.yml` — `활성 고객`, `not_covered: 직원 급여`
  - [ ] 상대 기간(`작년`, `올해`) — 데이터 최대 연도 기준으로 정의
  - [ ] 순위 용어(`베스트셀러`, `인기 있는`)
  - [ ] `not_covered` 추가: 원가/마진, 재고, 스트리밍 재생수, 고객 연령/성별

```powershell
..\.venv\Scripts\python.exe -m src.ontology.loader   # 로딩 + 무결성 검증
```

검증 항목: 엔티티 이름 중복 / 관계의 from·to 존재 여부 / 지표의 entity 존재 여부 /
`entity.attribute` 형식의 dimension 참조 / 실제 마트 테이블과의 정합성.

---

## 5단계 — 온톨로지 컴파일러

`src/ontology/compiler.py`. **이 파일이 프로젝트의 두뇌입니다.** 온톨로지는 데이터일 뿐이고,
그걸 LLM이 쓸 수 있는 형태로 바꾸는 게 여기입니다.

- [ ] `to_documents()` — 온톨로지 → 검색 문서 (`kind`: entity / metric / term / not_covered)
  - 엔티티 문서: label, description, synonyms, grain, 각 attribute의 label/synonyms/sample_values
  - 지표 문서: label, description, synonyms, dimensions. **expression은 넣지 말 것** (검색 노이즈)
  - not_covered 문서: 이게 잡히면 SQL 생성 없이 거절
- [ ] `build_join_sql()` — 선택된 엔티티들 → `FROM ... LEFT JOIN ...` 문자열
  - base(팩트=`sales`)를 FROM에 두고 나머지는 relationships에서 경로를 찾아 JOIN
  - 관계가 없으면 **반드시 예외를 던질 것.** 조용히 빠뜨리면 LLM이 데카르트 곱을 만듭니다
  - (선택) 1홉으로 안 닿는 엔티티는 관계 그래프에서 BFS로 최단 경로 탐색
- [ ] `render_context()` — 검색된 조각들 → 프롬프트 텍스트
  - 사용 가능한 테이블 / 조인 방법 / 지표 정의 / 용어 정의 순서
  - 지표 expression은 **복사해서 쓰라고** 명시 (LLM이 `SUM`을 `AVG`로 바꾸는 일이 실제로 일어납니다)

---

## 6단계 — 검색 인덱스

- [ ] `src/retrieval/index.py` — Chroma 인덱싱
  - `ids`를 명시해 **멱등하게** (재실행해도 중복이 안 쌓이게)
  - 문서 형식을 바꾸면 **컬렉션 이름도 바꾸기** (stale index 방지)
  - 생성자 파라미터는 `embedding`이 아니라 `embedding_function`
- [ ] `src/retrieval/search.py` — kind별 검색 + not_covered 차단
  - `similarity_search(..., filter={"kind": "entity"})` 로 종류별 분리 검색
  - not_covered는 `similarity_search_with_score`로 거리를 보고 임계값 이하면 `blocked_reason` 채우고 즉시 반환
  - 임계값은 직접 실험: bge-m3 기준 0.9~1.1 근처에서 시작해
    "연봉 얼마야?"는 걸리고 "매출 얼마야?"는 안 걸리는 값을 찾으세요

```powershell
# Ollama 임베딩 모델 준비
ollama pull bge-m3

..\.venv\Scripts\python.exe -m src.retrieval.index
```

---

## 7단계 — LangGraph 에이전트

**그래프 설계는 상태 설계가 8할입니다.** 노드를 짜기 전에 `state.py`부터 채우세요.

- [ ] `src/agent/state.py` — `entities`, `metrics`, `context`, `join_sql`, `blocked_reason`, `sql`, `error`, `df`, `attempts`, `answer`
- [ ] `src/agent/prompts.py` — SQL 생성 / 에러 수정 / 답변 프롬프트
- [ ] `src/agent/nodes.py` — `retrieve` / `generate` / `execute` / `answer` + 라우터
  - 노드 안에서 예외를 던지지 말 것. 실패는 상태에 담아야 재시도 루프를 돌릴 수 있습니다
- [ ] `src/agent/graph.py` — 그래프 조립

```
START -> retrieve ─┬─ 차단됨 ────────────────────→ answer -> END
                   └─ 정상 → generate → execute ─┬─ 성공 → answer
                                  ↑              └─ 실패 ┘
                                  └──────────────────────┘
```

```powershell
..\.venv\Scripts\python.exe -m src.agent.graph
```

---

## 8단계 — 평가

`evals/questions.yml`을 카테고리별로 5개 이상씩 채웁니다.

- [ ] 기본 (단일 지표 + 단일 차원)
- [ ] 다중 조인
- [ ] 용어 해석이 필요한 질문 ("작년", "활성 고객")
- [ ] 거절해야 하는 질문 (`not_covered`)
- [ ] 함정 (주문 수 vs 주문 상세 줄 수)

프롬프트나 온톨로지를 고칠 때마다 **목록 전체를 돌려서** "고쳤더니 다른 게 깨지지 않았나"를 확인하세요.

---

## 막혔을 때

- 각 TODO 주석에 **힌트**와 **참고할 파일**이 적혀 있습니다
- YAML에 어떤 필드를 쓸 수 있는지 헷갈리면 [src/ontology/models.py](src/ontology/models.py)를 보세요. **dataclass 정의가 곧 YAML 스키마 계약서**입니다
- dbt 문법이 막히면 `dbt compile` 로 생성되는 SQL을 `dbt/target/compiled/` 에서 확인하세요
- 완성 예시가 있는 파일: `stg_customers.sql`, `dim_customer.sql`, `entities.yml`의 `customer`, `metrics.yml`의 `total_revenue`, `src/ontology/models.py`
