with base as (

    select *
    from {{ ref('int_applicant_risk_base') }}

),

ratios as (

    select
        *,

        case
            when AMT_INCOME_TOTAL is null
              or AMT_INCOME_TOTAL = 0
              or AMT_CREDIT is null
                then null
            else AMT_CREDIT / AMT_INCOME_TOTAL
        end as CREDIT_INCOME_RATIO,

        case
            when AMT_INCOME_TOTAL is null
              or AMT_INCOME_TOTAL = 0
              or AMT_ANNUITY is null
                then null
            else AMT_ANNUITY / AMT_INCOME_TOTAL
        end as ANNUITY_INCOME_RATIO

    from base

),

features as (

    select
        *,

        /* Affordability burden */
        case
            when ANNUITY_INCOME_RATIO is null
                then 'Unknown'
            when ANNUITY_INCOME_RATIO <= 0.1148
                then 'Low burden'
            when ANNUITY_INCOME_RATIO <= 0.1628
                then 'Moderate burden'
            when ANNUITY_INCOME_RATIO <= 0.2291
                then 'Elevated burden'
            else 'High burden'
        end as AFFORDABILITY_SEGMENT,

        /* Broad repayment grouping */
        case
            when HAS_REPAYMENT_HISTORY = 0
                then 'No history'
            when OBSERVED_PAYMENT_COUNT = 0
                then 'No observed payments'
            when LATE_PAYMENT_RATE = 0
             and UNDERPAYMENT_RATE = 0
                then 'Clean observed history'
            else 'Observed repayment issue'
        end as REPAYMENT_SEGMENT,

        /* Specific repayment behavior */
        case
            when HAS_REPAYMENT_HISTORY = 0
                then 'No history'
            when OBSERVED_PAYMENT_COUNT = 0
                then 'No observed payments'
            when LATE_PAYMENT_RATE = 0
             and UNDERPAYMENT_RATE = 0
                then 'Neither issue'
            when LATE_PAYMENT_RATE > 0
             and UNDERPAYMENT_RATE = 0
                then 'Late only'
            when LATE_PAYMENT_RATE = 0
             and UNDERPAYMENT_RATE > 0
                then 'Underpayment only'
            when LATE_PAYMENT_RATE > 0
             and UNDERPAYMENT_RATE > 0
                then 'Both issues'
            else 'Unavailable'
        end as REPAYMENT_PATTERN,

        /* Late-payment severity */
        case
            when HAS_REPAYMENT_HISTORY = 0
                then 'No history'
            when OBSERVED_PAYMENT_COUNT = 0
                then 'No observed payments'
            when LATE_PAYMENT_RATE = 0
                then 'None'
            when LATE_PAYMENT_RATE <= 0.0492
                then 'Low'
            when LATE_PAYMENT_RATE <= 0.1020
                then 'Moderate'
            when LATE_PAYMENT_RATE <= 0.2000
                then 'Elevated'
            else 'High'
        end as LATE_PAYMENT_SEVERITY,

        /* Underpayment severity */
        case
            when HAS_REPAYMENT_HISTORY = 0
                then 'No history'
            when OBSERVED_PAYMENT_COUNT = 0
                then 'No observed payments'
            when UNDERPAYMENT_RATE = 0
                then 'None'
            when UNDERPAYMENT_RATE <= 0.0656
                then 'Low'
            when UNDERPAYMENT_RATE <= 0.1379
                then 'Moderate'
            when UNDERPAYMENT_RATE <= 0.2799
                then 'Elevated'
            else 'High'
        end as UNDERPAYMENT_SEVERITY

    from ratios

)

select *
from features