with segments as (

    select *
    from {{ ref('applicant_risk_segments') }}

),

summary as (

    select
        RISK_TIER,

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
        ) as AVG_RISK_SCORE,

        round(
            min(RISK_SCORE),
            2
        ) as MIN_RISK_SCORE,

        round(
            max(RISK_SCORE),
            2
        ) as MAX_RISK_SCORE

    from segments

    group by RISK_TIER

)

select *
from summary