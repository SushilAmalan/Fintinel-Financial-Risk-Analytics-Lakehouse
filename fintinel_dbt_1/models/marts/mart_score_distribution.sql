with scored as (

    select
        SK_ID_CURR,
        TARGET,
        RISK_SCORE,
        RISK_TIER

    from {{ ref('applicant_risk_segments') }}

    where RISK_SCORE is not null

),

distribution as (

    select
        RISK_SCORE,
        RISK_TIER,

        count(*) as APPLICANTS,

        round(
            100.0 * count(*) / sum(count(*)) over (),
            4
        ) as PCT_OF_SCORED_APPLICANTS,

        sum(TARGET) as TARGET_1_COUNT,

        round(
            100.0 * avg(TARGET),
            4
        ) as TARGET_1_RATE

    from scored

    group by
        RISK_SCORE,
        RISK_TIER

)

select *
from distribution