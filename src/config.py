"""프로젝트 전역 설정. 완성본이니 수정 없이 쓰세요.

.env 를 읽어 상수로 노출합니다. 다른 모듈은 os.environ 을 직접 읽지 말고
여기서 import 하세요. 설정이 흩어지면 나중에 반드시 후회합니다.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = PROJECT_ROOT / "ontology"
DBT_DIR = PROJECT_ROOT / "dbt"
EVALS_DIR = PROJECT_ROOT / "evals"

load_dotenv(PROJECT_ROOT / ".env")


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


# --- PostgreSQL ---
PG_HOST = _env("PGHOST", "localhost")
PG_PORT = _env("PGPORT", "5432")
PG_DATABASE = _env("PGDATABASE", "analytics")
PG_USER = _env("PGUSER", "dbt")
PG_PASSWORD = _env("PGPASSWORD", "dbt_password")

# 에이전트가 쓸 읽기 전용 계정. 없으면 dbt 계정으로 폴백합니다.
PG_READONLY_USER = _env("PG_READONLY_USER") or PG_USER
PG_READONLY_PASSWORD = _env("PG_READONLY_PASSWORD") or PG_PASSWORD

MARTS_SCHEMA = f"{_env('DBT_SCHEMA', 'analytics')}_marts"


def pg_url(readonly: bool = True) -> str:
    user = PG_READONLY_USER if readonly else PG_USER
    password = PG_READONLY_PASSWORD if readonly else PG_PASSWORD
    return f"postgresql+psycopg://{user}:{password}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"


# --- LLM ---
LLM_MODEL = _env("LLM_MODEL", "openai/gpt-oss-120b")
LLM_BASE_URL = _env("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = _env("GROQ_API_KEY")

# --- 임베딩 ---
EMBEDDING_MODEL = _env("EMBEDDING_MODEL", "bge-m3")
OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434")

# --- 벡터 스토어 ---
CHROMA_DIR = str(PROJECT_ROOT / _env("CHROMA_DIR", "./.chroma").lstrip("./"))
CHROMA_COLLECTION = _env("CHROMA_COLLECTION", "ontology_v1")
