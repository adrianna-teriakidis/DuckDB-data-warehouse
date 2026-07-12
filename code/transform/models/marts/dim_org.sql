with stg as (

    select * from {{ ref('stg_ae_data') }}

),

latest_period as (

    select max(period_date) as period_date from stg

),

-- an org's parent as of the most recent period only - if the org isn't
-- present in that period (e.g. it closed or merged), it has no "current" parent
current_parent as (

    select
        stg.org_code,
        stg.parent_org as current_parent_org
    from stg
    inner join latest_period on stg.period_date = latest_period.period_date

),

-- unlike parent org, a name doesn't go stale just because the org wasn't in
-- the latest file - carry forward whatever name it last reported under
most_recent_name as (

    select distinct
        org_code,
        first_value(org_name) over (
            partition by org_code order by period_date desc
        ) as current_org_name
    from stg

),

orgs as (

    select distinct org_code from stg

)

select
    orgs.org_code,
    coalesce(current_parent.current_parent_org, 'No current assignment') as current_parent_org,
    most_recent_name.current_org_name
from orgs
left join current_parent on orgs.org_code = current_parent.org_code
left join most_recent_name on orgs.org_code = most_recent_name.org_code

