select *
from {{ ref('applicant_risk_scores') }}
where
       (SCORE_STATUS = 'Full score' and RISK_SCORE is null)
    or (SCORE_STATUS <> 'Full score' and RISK_SCORE is not null)