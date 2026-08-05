-- ✅ 완성 예시입니다.
--
-- dimension(차원) 테이블 = "누가 / 무엇을 / 어디서" 를 설명하는 테이블.
-- 한 행 = 고객 1명. 중복이 없어야 합니다.
--
-- 여기서 담당 직원 이름까지 미리 붙여둡니다. 그러면 온톨로지에서
-- "고객의 담당자" 를 물었을 때 LLM이 employee 테이블을 조인할 필요가 없습니다.

with customers as (

    select * from {{ ref('stg_customers') }}

),

employees as (

    select employee_id, full_name from {{ ref('stg_employees') }}

)

select
    customers.customer_id,
    customers.full_name          as customer_name,
    customers.email,
    customers.city               as customer_city,
    customers.state              as customer_state,
    customers.country            as customer_country,
    customers.employee_id        as support_rep_id,
    employees.full_name          as support_rep_name

from customers
left join employees using (employee_id)
