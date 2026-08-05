-- TODO: raw.invoice_line 을 정리하세요.
--
-- 원본 컬럼: invoice_line_id, invoice_id, track_id, unit_price, quantity
--
-- 힌트:
--   - 매출 금액은 원본에 없습니다. 여기서 만드세요:
--       unit_price * quantity as line_amount
--     이 한 줄이 나중에 metrics.yml 의 total_revenue 가 참조할 컬럼입니다.
--   - unit_price 는 numeric 으로 캐스팅해 두세요. float 로 두면 합계에서 오차가 납니다.

with source as (

    select * from {{ source('chinook_raw', 'invoice_line') }}

),

renamed as (

    select
        invoice_line_id,
        invoice_id,
        track_id,
        unit_price::numeric,
        quantity,
        unit_price::numeric * quantity as line_amount
    from source

)

select * from renamed
