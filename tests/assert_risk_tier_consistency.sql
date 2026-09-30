select *
from {{ ref('applicant_risk_segments') }}
where
       (RISK_SCORE is null and RISK_TIER <> 'Unavailable')

    or (RISK_SCORE is not null and RISK_SCORE <= 17.50
        and RISK_TIER <> 'Low')

    or (RISK_SCORE > 17.50 and RISK_SCORE <= 30.00
        and RISK_TIER <> 'Moderate')

    or (RISK_SCORE > 30.00 and RISK_SCORE <= 55.00
        and RISK_TIER <> 'Elevated')

    or (RISK_SCORE > 55.00
        and RISK_TIER <> 'High')