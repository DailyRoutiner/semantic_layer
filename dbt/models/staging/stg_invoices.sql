-- TODO: raw.invoice 를 정리하세요. 참고: stg_customers.sql
--
-- 원본 컬럼(적재 후 snake_case):
--   invoice_id, customer_id, invoice_date, billing_address, billing_city,
--   billing_state, billing_country, billing_postal_code, total
--
-- 힌트:
--   - invoice_date 는 SQLite에서 문자열로 넘어옵니다. ::timestamp 로 캐스팅하세요.
--   - 날짜 분석용 파생 컬럼을 미리 만들어 두면 LLM이 편해집니다:
--       date_trunc('month', invoice_date::timestamp) as invoice_month
--       extract(year from invoice_date::timestamp)::int as invoice_year
--   - total 은 invoice_line 합계와 중복되는 값입니다. 이름을 invoice_total 로 두어
--     fct_sales 의 line_amount 와 헷갈리지 않게 하세요.

with source as (

    select * from {{ source('chinook_raw', 'invoice') }}

),

renamed as (

    select
        invoice_id,
        customer_id,
        invoice_date::timestamp,
        date_trunc('month', invoice_date::timestamp) as invoice_month,
        extract(year from invoice_date::timestamp) as invoice_year, 
        billing_address, billing_city, billing_state, billing_country, billing_postal_code,
        total as invoice_total

    from source

)

select * from renamed
