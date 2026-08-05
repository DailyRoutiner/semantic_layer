-- TODO: 판매 팩트 테이블. **이 프로젝트에서 가장 중요한 모델입니다.**
--
-- fact(팩트) 테이블 = "무슨 일이 일어났는가" 를 기록하는 테이블.
-- 한 행 = 주문 상세 1줄 (= invoice_line 1행).
--
-- 왜 invoice 가 아니라 invoice_line 단위인가:
--   가장 잘게 쪼갠 단위(grain)로 만들어야 어떤 질문에도 답할 수 있습니다.
--   invoice 단위로 만들면 "장르별 매출"을 영원히 못 구합니다.
--   **팩트 테이블의 grain 을 정하는 것이 데이터 모델링의 첫 번째 결정입니다.**
--
-- 필요한 컬럼:
--   [키]     sales_id(= invoice_line_id), invoice_id, customer_id, track_id, employee_id
--   [측정값] quantity, unit_price, line_amount
--   [날짜]   invoice_date, invoice_month, invoice_year
--   [편의]   country (= 청구 국가. 자주 쓰이므로 여기 둡니다)
--
-- 힌트:
--   with lines as (select * from {{ ref('stg_invoice_lines') }}),
--        invoices as (select * from {{ ref('stg_invoices') }}),
--        customers as (select * from {{ ref('stg_customers') }})
--   - lines 를 기준으로 invoices 를 inner join (주문 없는 상세는 없어야 정상)
--   - employee_id 는 customers 를 거쳐 가져옵니다 (담당 영업사원)
--   - 차원의 '이름'은 여기에 넣지 마세요. track_name, customer_name 은
--     dim_track / dim_customer 에 있습니다. 팩트에는 키와 숫자만 둡니다.
--     (이 규칙을 지켜야 스타 스키마가 유지됩니다)

with lines as (
    select * from {{ ref('stg_invoice_lines')}}
),
invoice as (
    select * from {{ ref('stg_invoices')}}
),
customer as (
    select * from {{ ref('stg_customers')}}
)
select invoice_line_id as sales_id, invoice_id, customer_id, track_id, employee_id,
    quantity, unit_price, line_amount,
    invoice_date, invoice_month, invoice_year,
    country
from lines a
    join invoice b using (invoice_id)
    left join customer using (customer_id)
