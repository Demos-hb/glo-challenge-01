with hires_2021 as (
  select
    department_id,
    count(1) as hires_count
  from `iter-data-storage-pv-uat.temp.hired_employees`
  where extract(year from datetime) = 2021
    and department_id is not null
  group by department_id
),
mean_hires_2021 as (
  select
    avg(hires_count) as avg_hires
  from hires_2021
),
hires_history as (
  select
    department_id,
    count(1) as hires_count
  from `iter-data-storage-pv-uat.temp.hired_employees`
  where department_id is not null
  group by department_id
)
select
  h.department_id as id,
  d.department,
  h.hires_count
from hires_history h
cross join mean_hires_2021 a
inner join `iter-data-storage-pv-uat.temp.departments` d
  on h.department_id = d.id  
where h.hires_count > a.avg_hires
order by h.hires_count desc;
