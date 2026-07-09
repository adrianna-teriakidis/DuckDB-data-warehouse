with source as (

    select * from {{ source('raw', 'ae_data') }}

),

renamed as (

    select
        "Period" as period,
        "Org Code" as org_code,
        "Parent Org" as parent_org,
        "Org name" as org_name,
        -- pre-2019 files use "Number of A&E attendances ..." / "Number of attendances
        -- over 4hrs ..." instead of the current wording for the same metrics
        coalesce("A&E attendances Type 1", "Number of A&E attendances Type 1") as ae_attendances_type_1,
        coalesce("A&E attendances Type 2", "Number of A&E attendances Type 2") as ae_attendances_type_2,
        coalesce("A&E attendances Other A&E Department", "Number of A&E attendances Other A&E Department") as ae_attendances_other,
        "A&E attendances Booked Appointments Type 1" as ae_attendances_booked_type_1,
        "A&E attendances Booked Appointments Type 2" as ae_attendances_booked_type_2,
        "A&E attendances Booked Appointments Other Department" as ae_attendances_booked_other,
        coalesce("Attendances over 4hrs Type 1", "Number of attendances over 4hrs Type 1") as attendances_over_4hrs_type_1,
        coalesce("Attendances over 4hrs Type 2", "Number of attendances over 4hrs Type 2") as attendances_over_4hrs_type_2,
        coalesce("Attendances over 4hrs Other Department", "Number of attendances over 4hrs Other A&E Department") as attendances_over_4hrs_other,
        "Attendances over 4hrs Booked Appointments Type 1" as attendances_over_4hrs_booked_type_1,
        "Attendances over 4hrs Booked Appointments Type 2" as attendances_over_4hrs_booked_type_2,
        "Attendances over 4hrs Booked Appointments Other Department" as attendances_over_4hrs_booked_other,
        "Patients who have waited 4-12 hs from DTA to admission" as patients_waited_4_12hrs_dta,
        "Patients who have waited 12+ hrs from DTA to admission" as patients_waited_12plus_hrs_dta,
        "Emergency admissions via A&E - Type 1" as emergency_admissions_type_1,
        "Emergency admissions via A&E - Type 2" as emergency_admissions_type_2,
        "Emergency admissions via A&E - Other A&E department" as emergency_admissions_other,
        "Other emergency admissions" as other_emergency_admissions,
        strptime(
            split_part("Period", '-', 2) || ' ' || split_part("Period", '-', 3),
            '%B %Y'
        )::date as period_date
    from source
    -- each monthly file includes a national "TOTAL" summary row alongside
    -- the real per-organization rows; drop it so downstream aggregations
    -- don't double-count against the real orgs that already sum to it.
    -- NHS isn't consistent about casing across years ("TOTAL", "Total", "TOTAl"),
    -- so compare case-insensitively rather than to the exact string "TOTAL"
    where upper(trim("Org Code")) != 'TOTAL'

)

select * from renamed
