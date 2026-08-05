"""프롬프트 모음.

프롬프트를 코드에 흩어 두지 말고 여기 모으세요.
튜닝할 때 한 파일만 열면 되고, 나중에 버전 관리도 쉽습니다.

프로젝트 1과 결정적으로 다른 점:
    프로젝트 1: "스키마를 줄 테니 알아서 SQL 을 짜라"
    프로젝트 2: "테이블·조인·지표식을 다 줄 테니 조립만 해라"

    LLM 의 자유도를 줄일수록 정확도가 올라갑니다.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

# ─────────────────────────────────────────────────────────────
# TODO 1: SQL 생성 프롬프트
#
# 반드시 넣어야 할 지시:
#   - 아래 '조인 방법' 절을 그대로 사용할 것. 다른 조인을 만들지 말 것
#   - 지표는 '지표 정의'에 있는 식을 그대로 복사할 것. 변형 금지
#   - 컨텍스트에 없는 테이블/컬럼은 존재하지 않는다고 간주할 것
#   - PostgreSQL 문법 (프로젝트 1은 SQLite 였습니다. date_trunc, INTERVAL, ILIKE 등이 다릅니다)
#   - SELECT 만. LIMIT 필수
#   - SQL 만 출력. 코드펜스·설명 금지
#
# 힌트: 컨텍스트를 {context}, 조인을 {join_sql} 로 따로 받으면
#      "조인은 이거 그대로 써" 라는 지시가 훨씬 잘 먹힙니다.
# ─────────────────────────────────────────────────────────────
SQL_SYSTEM = """TODO"""

sql_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SQL_SYSTEM),
        ("human", "{question}"),
    ]
)


# ─────────────────────────────────────────────────────────────
# TODO 2: SQL 수리 프롬프트
#   실패한 SQL + 에러 메시지를 주고 고치게 합니다.
#   프로젝트 1의 fix_prompt 를 가져오되, 컨텍스트를 온톨로지 기반으로 바꾸세요.
# ─────────────────────────────────────────────────────────────
FIX_SYSTEM = """TODO"""

fix_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", FIX_SYSTEM),
        ("human", "질문: {question}\n\n실패한 SQL:\n{sql}\n\n오류:\n{error}"),
    ]
)


# ─────────────────────────────────────────────────────────────
# TODO 3: 답변 생성 프롬프트
#   "쿼리 결과에 있는 사실만 말할 것" 을 반드시 넣으세요.
#   추가로 이번엔 "어떤 지표 정의를 썼는지 한 줄로 밝힐 것" 을 넣어보세요.
#     예: "총매출(SUM(line_amount)) 기준입니다."
#   사용자가 숫자의 근거를 알 수 있어야 신뢰가 생깁니다.
# ─────────────────────────────────────────────────────────────
ANSWER_SYSTEM = """TODO"""

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ANSWER_SYSTEM),
        ("human", "질문: {question}\n\nSQL:\n{sql}\n\n결과:\n{result}"),
    ]
)
