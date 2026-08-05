-- ✅ 완성 예시입니다. 나머지 stg_*.sql 은 이 패턴을 보고 직접 작성하세요.
--
-- staging 계층의 역할은 딱 네 가지입니다. 그 이상은 하지 마세요.
--   1. 컬럼 이름 정리 (support_rep_id -> employee_id 처럼 의미를 명확히)
--   2. 타입 캐스팅
--   3. 가벼운 파생 컬럼 (이름 합치기 등)
--   4. 불필요한 컬럼 제거
--
-- 하지 말아야 할 것: 조인, 집계, 필터링. 그건 marts 의 일입니다.

with source as (

    select * from {{ source('chinook_raw', 'customer') }}

),

renamed as (

    select
        customer_id,
        first_name,
        last_name,
        first_name || ' ' || last_name as full_name,
        company,
        city,
        state,
        country,
        postal_code,
        email,
        phone,
        support_rep_id as employee_id   -- 담당 영업사원. 이름을 의미에 맞게 바꿉니다

    from source

)

select * from renamed
