

--select * from iter-data-storage-pv-uat.temp.hired_employees;
--select * from iter-data-storage-pv-uat.temp.departments;
--select * from iter-data-storage-pv-uat.temp.jobs;

--select count(1) from iter-data-storage-pv-uat.temp.hired_employees; -- 1998
--select count(1) from iter-data-storage-pv-uat.temp.departments; -- 11
select count(1) from iter-data-storage-pv-uat.temp.jobs; -- 182





--select *
select department, job, EXTRACT(QUARTER FROM e.datetime) AS quarter, count(distinct e.id) cant_reg
from iter-data-storage-pv-uat.temp.hired_employees e
left join iter-data-storage-pv-uat.temp.departments d
on d.id = e.department_id
left join iter-data-storage-pv-uat.temp.jobs j
on j.id = e.department_id
where department is not null and job is not null and e.datetime is not null
group by department, job, quarter
order by department, job






with vista
as
(
select *,
case when quarter = 1 then 'Q1' else
case when quarter = 2 then 'Q2' else
case when quarter = 3 then 'Q3' else
case when quarter = 4 then 'Q4' else 'Q0'
end end end end as quarter_desc
from(
  select department, job, EXTRACT(QUARTER FROM e.datetime) AS quarter, count(distinct e.id) cant_reg
  from iter-data-storage-pv-uat.temp.hired_employees e
  left join iter-data-storage-pv-uat.temp.departments d
  on d.id = e.department_id
  left join iter-data-storage-pv-uat.temp.jobs j
  on j.id = e.department_id
  where department is not null and job is not null and e.datetime is not null
  group by department, job, quarter
  order by department, job
)
),
tabla_pivot as
(
select * except (quarter)
from vista
PIVOT (
  SUM(cant_reg) FOR quarter_desc IN ('Q1', 'Q2', 'Q3', 'Q4')
)
)
select department, job,
sum(Q1) as Q1,
sum(Q2) as Q2,
sum(Q3) as Q3,
sum(Q4) as Q4
from tabla_pivot
group by department, job
order by department, job
;
