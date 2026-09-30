with segments as (

    select
        SK_ID_CURR,
        TARGET,
        AFFORDABILITY_SEGMENT,
        REPAYMENT_SEGMENT,
        RISK_SCORE

    from {{ ref('applicant_risk_segments') }}

),

summary as (

    select
        AFFORDABILITY_SEGMENT,
        REPAYMENT_SEGMENT,

        count(*) as APPLICANTS,

        round(
            100.0 * count(*) / sum(count(*)) over (),
            4
        ) as PCT_OF_TOTAL_APPLICANTS,

        count(RISK_SCORE) as SCORED_APPLICANTS,

        sum(TARGET) as TARGET_1_COUNT,

        round(
            100.0 * avg(TARGET),
            4
        ) as TARGET_1_RATE,

        round(
            avg(RISK_SCORE),
            2
        ) as AVG_RISK_SCORE

    from segments

    group by
        AFFORDABILITY_SEGMENT,
        REPAYMENT_SEGMENT

)

select *
from summary