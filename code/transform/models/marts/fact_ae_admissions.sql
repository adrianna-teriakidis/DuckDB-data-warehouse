with stg as (

    select * from {{ ref('stg_ae_data') }}

),

admissions as (

    select
        period,
        period_date,
        org_code,
        org_name,
        parent_org,
        emergency_admissions_type_1
            + emergency_admissions_type_2
            + emergency_admissions_other as total_emergency_admissions,
        -- admissions not via any A&E department at this provider (e.g. direct GP
        -- referral) — a separate population, not part of the total above
        other_emergency_admissions,
        patients_waited_4_12hrs_dta as admissions_waited_4_12hrs,
        patients_waited_12plus_hrs_dta as admissions_waited_12plus_hrs
    from stg

)

select * from admissions
