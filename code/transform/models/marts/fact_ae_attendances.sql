with stg as (

    select * from {{ ref('stg_ae_data') }}
    where has_ae_attendance_data

),

-- one row per org per month per (type, booked) combination, so the
-- viz layer can filter/group by either dimension via dropdown
unpivoted as (

    select
        period, period_date, org_code, org_name, parent_org,
        'Type 1' as type, 'unplanned' as booked,
        ae_attendances_type_1 as attendances,
        attendances_over_4hrs_type_1 as attendances_over_4hrs
    from stg

    union all

    select
        period, period_date, org_code, org_name, parent_org,
        'Type 2' as type, 'unplanned' as booked,
        ae_attendances_type_2 as attendances,
        attendances_over_4hrs_type_2 as attendances_over_4hrs
    from stg

    union all

    select
        period, period_date, org_code, org_name, parent_org,
        'Other' as type, 'unplanned' as booked,
        ae_attendances_other as attendances,
        attendances_over_4hrs_other as attendances_over_4hrs
    from stg

    union all

    select
        period, period_date, org_code, org_name, parent_org,
        'Type 1' as type, 'booked' as booked,
        ae_attendances_booked_type_1 as attendances,
        attendances_over_4hrs_booked_type_1 as attendances_over_4hrs
    from stg

    union all

    select
        period, period_date, org_code, org_name, parent_org,
        'Type 2' as type, 'booked' as booked,
        ae_attendances_booked_type_2 as attendances,
        attendances_over_4hrs_booked_type_2 as attendances_over_4hrs
    from stg

    union all

    select
        period, period_date, org_code, org_name, parent_org,
        'Other' as type, 'booked' as booked,
        ae_attendances_booked_other as attendances,
        attendances_over_4hrs_booked_other as attendances_over_4hrs
    from stg

)

select * from unpivoted
