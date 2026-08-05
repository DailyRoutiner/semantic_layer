-- TODO: 직원 차원 테이블. 한 행 = 직원 1명.
--
-- 필요한 컬럼:
--   employee_id, employee_name, job_title, hire_date, country,
--   manager_id, manager_name
--
-- 힌트:
--   - manager_name 은 stg_employees 를 자기 자신과 조인해서 얻습니다 (self join).
--       from employees e
--       left join employees m on e.manager_id = m.employee_id
--   - 프로젝트 1에서 "관리자가 누구야?" 질문이 self join 때문에 어려웠던 걸 기억하세요.
--     여기서 한 번 해결해두면 LLM은 manager_name is not null 만 쓰면 됩니다.

with employee as(
    select 
        employee_id, manager_id,
        full_name as employee_name,
        job_title, hire_date,
        country
    from {{ ref('stg_employees') }}
)
select 
  a.employee_id, a.employee_name, a.job_title, a.hire_date, a.country,
  a.manager_id, b.employee_name as manager_name
from employee a
    left join employee b on a.manager_id = b.employee_id
