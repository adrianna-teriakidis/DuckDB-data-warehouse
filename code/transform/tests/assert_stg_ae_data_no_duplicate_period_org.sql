-- dbt fails this test if it returns any rows: more than one row per
-- (period, org_code) would mean the same org was double-counted for a month.
select
    period,
    org_code,
    count(*) as row_count
from {{ ref('stg_ae_data') }}
group by period, org_code
having count(*) > 1
