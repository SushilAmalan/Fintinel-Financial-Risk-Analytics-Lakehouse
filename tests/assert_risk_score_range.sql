select *
from {{ ref('applicant_risk_scores') }}
where
    RISK_SCORE is not null
    and (RISK_SCORE < 0 or RISK_SCORE > 100)