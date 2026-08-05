from __future__ import annotations

import pandas as pd
import re
from sqlalchemy import create_engine, text

from src.config import MARTS_SCHEMA, pg_url

ALLOWED_START = {"select", "with"}


# ─────────────────────────────────────────────────────────────
# TODO 1: 읽기 전용 엔진 만들기
#
#   engine = create_engine(pg_url(readonly=True), pool_pre_ping=True)
#
#   그리고 Postgres 에 읽기 전용 계정을 실제로 만들어야 합니다.
#   docker compose exec postgres psql -U dbt -d analytics 로 들어가서:
#
#     CREATE USER rag_reader WITH PASSWORD 'rag_reader_password';
#     GRANT USAGE ON SCHEMA analytics_marts TO rag_reader;
#     GRANT SELECT ON ALL TABLES IN SCHEMA analytics_marts TO rag_reader;
#     ALTER DEFAULT PRIVILEGES IN SCHEMA analytics_marts
#       GRANT SELECT ON TABLES TO rag_reader;
#
#   staging/raw 스키마에는 권한을 주지 마세요.
#   에이전트가 마트만 보게 하는 것 자체가 설계입니다.
# ─────────────────────────────────────────────────────────────
engine = create_engine(pg_url(readonly=True), pool_pre_ping=True)


def strip_leading_noise(sql: str) -> str:
    """앞쪽 주석과 여는 괄호를 제거해 첫 키워드를 노출시킨다.

    프로젝트 1에서 만든 것과 동일합니다. 그대로 옮겨오세요.
    """
    s = sql.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s).strip()

    while True:
        if s.startswith("--"):
            _, _, s = s.partition("\n") # 줄 끝까지 버림
            s = s.lstrip()
        elif s.startswith("/*"):
            end = s.find("*/")
            if end == -1:
                break

            s = s[end + 2:].lstrip()
        else:
            break
    return s

def first_keyword(sql:str) :
    s = strip_leading_noise(sql).lstrip("( \t\r\n")

    parts = s.split(None, 1)
    return parts[0].lower() if parts else ""


def run_sql(sql: str, limit: int = 50) -> pd.DataFrame:
    """SELECT/WITH 만 허용하고 결과를 DataFrame 으로 돌려준다.

    방어는 3겹입니다. 하나라도 빼지 마세요.
      1) DB 권한   — rag_reader 는 SELECT 만 가능       <- 가장 강력
      2) 접두사 검사 — select / with 로 시작하는지
      3) 행수 제한  — fetchmany 로 limit 만큼만

    힌트: SQLAlchemy 2.0 에서는 raw 문자열이 아니라 text(sql) 을 넘겨야 합니다.
    """
    cleaned = strip_leading_noise(sql)

    if first_keyword(cleaned) in ALLOWED_START:

        with engine.connect() as conn:
            cursor = conn.execute(text(cleaned))
            columns = list(cursor.keys())
            rows = cursor.fetchmany(limit)
        return pd.DataFrame(rows, columns=columns)
    else:
        raise ValueError(
            f"select with 키워드가 아닙니다."
        )


def list_mart_tables() -> list[str]:
    """마트 스키마의 테이블 목록. 온톨로지가 실제 테이블과 맞는지 검증할 때 씁니다."""
    query = text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = :schema ORDER BY table_name"
    )
    with engine.connect() as conn:
        return [row[0] for row in conn.execute(query, {"schema": MARTS_SCHEMA})]


if __name__ == "__main__":
    print(f"마트 스키마: {MARTS_SCHEMA}")
    print("테이블:", list_mart_tables())
