select *
from {{ ref('int_applicant_risk_base') }}
where
       (LATE_PAYMENT_RATE is not null
        and (LATE_PAYMENT_RATE < 0 or LATE_PAYMENT_RATE > 1))

    or (UNDERPAYMENT_RATE is not null
        and (UNDERPAYMENT_RATE < 0 or UNDERPAYMENT_RATE > 1))