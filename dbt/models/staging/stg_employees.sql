-- TODO: raw.employee 를 정리하세요.
--
-- 원본 컬럼: employee_id, last_name, first_name, title, reports_to, birth_date,
--            hire_date, address, city, state, country, postal_code, phone, fax, email
--
-- 힌트:
--   - full_name 파생 (stg_customers 참고)
--   - reports_to -> manager_id 로 이름을 바꾸면 의미가 분명해집니다
--   - title 은 직급입니다. job_title 로 바꾸세요 (track.title 과 헷갈림 방지)
--   - birth_date, hire_date 는 ::date 캐스팅

with source as (

    select * from {{ source('chinook_raw', 'employee') }}

)

select
    employee_id,
    last_name,
    first_name, 
    last_name || ' ' || first_name as full_name,
    title as job_title, 
    reports_to as manager_id,
    birth_date::date,
    hire_date::date,
    address,
    city,
    state,
    country,
    postal_code,
    phone,
    fax,
    email

from source
