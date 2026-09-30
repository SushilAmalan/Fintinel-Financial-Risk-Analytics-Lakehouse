with features as (

    select *
    from {{ ref('int_applicant_risk_features') }}

),

components as (

    select
        *,

        case LATE_PAYMENT_SEVERITY
            when 'None' then 0
            when 'Low' then 1
            when 'Moderate' then 2
            when 'Elevated' then 3
            when 'High' then 4
            else null
        end as LATE_LEVEL,

        case UNDERPAYMENT_SEVERITY
            when 'None' then 0
            when 'Low' then 1
            when 'Moderate' then 2
            when 'Elevated' then 3
            when 'High' then 4
            else null
        end as UNDERPAYMENT_LEVEL,

        case AFFORDABILITY_SEGMENT
            when 'Low burden' then 0
            when 'Moderate burden' then 10
            when 'Elevated burden' then 20
            when 'High burden' then 30
            else null
        end as AFFORDABILITY_SCORE

    from features

),

scored as (

    select
        *,

        case
            when HAS_REPAYMENT_HISTORY = 0
                then null

            when OBSERVED_PAYMENT_COUNT = 0
                then null

            when AFFORDABILITY_SCORE is null
                then null

            else round(
                (
                    (
                        (LATE_LEVEL + UNDERPAYMENT_LEVEL) / 2.0
                    ) / 4.0
                ) * 70.0,
                2
            )
        end as BEHAVIOR_SCORE

    from components

),

final as (

    select
        *,

        case
            when HAS_REPAYMENT_HISTORY = 0
                then 'No repayment history'

            when OBSERVED_PAYMENT_COUNT = 0
                then 'No observed payments'

            when AFFORDABILITY_SCORE is null
                then 'Missing affordability data'

            else 'Full score'
        end as SCORE_STATUS,

        case
            when HAS_REPAYMENT_HISTORY = 0
              or OBSERVED_PAYMENT_COUNT = 0
              or AFFORDABILITY_SCORE is null
                then null

            else round(
                BEHAVIOR_SCORE + AFFORDABILITY_SCORE,
                2
            )
        end as RISK_SCORE

    from scored

)

select *
from final