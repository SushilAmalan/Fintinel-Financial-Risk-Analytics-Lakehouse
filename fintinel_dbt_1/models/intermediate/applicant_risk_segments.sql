with scores as (

    select *
    from {{ ref('applicant_risk_scores') }}

),

segmented as (

    select
        *,

        case
            when RISK_SCORE is null
                then 'Unavailable'

            when RISK_SCORE <= 17.50
                then 'Low'

            when RISK_SCORE <= 30.00
                then 'Moderate'

            when RISK_SCORE <= 55.00
                then 'Elevated'

            else 'High'
        end as RISK_TIER

    from scores

)

select *
from segmented