with scores as (

    select
        SK_ID_CURR,
        TARGET,
        SCORE_STATUS,
        RISK_SCORE

    from {{ ref('applicant_risk_segments') }}

),

summary as (

    select
        SCORE_STATUS,

        count(*) as APPLICANTS,

        round(
            100.0 * count(*) / sum(count(*)) over (),
            4
        ) as PCT_OF_TOTAL_APPLICANTS,

        count(RISK_SCORE) as SCORED_APPLICANTS,

        count(*) - count(RISK_SCORE) as UNSCORED_APPLICANTS,

        sum(TARGET) as TARGET_1_COUNT,

        round(
            100.0 * avg(TARGET),
            4
        ) as TARGET_1_RATE,

        round(
            avg(RISK_SCORE),
            2
        ) as AVG_RISK_SCORE

    from scores

    group by SCORE_STATUS

)

select *
from summary