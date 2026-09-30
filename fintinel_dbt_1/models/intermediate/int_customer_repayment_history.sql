with credit_repayment as (

    select *
    from {{ ref('int_previous_credit_repayment') }}

),

customer_history as (

    select
        SK_ID_CURR,

        count(*) as PREVIOUS_CREDIT_COUNT,

        sum(TOTAL_INSTALLMENTS) as TOTAL_INSTALLMENTS,
        sum(OBSERVED_PAYMENT_COUNT) as OBSERVED_PAYMENT_COUNT,

        sum(LATE_PAYMENT_COUNT) as LATE_PAYMENT_COUNT,
        sum(UNDERPAYMENT_COUNT) as UNDERPAYMENT_COUNT,

        sum(TOTAL_SCHEDULED_AMOUNT) as TOTAL_SCHEDULED_AMOUNT,
        sum(TOTAL_PAID_AMOUNT) as TOTAL_PAID_AMOUNT,

        case
            when sum(OBSERVED_PAYMENT_COUNT) = 0 then null
            else
                sum(LATE_PAYMENT_COUNT)::float
                / sum(OBSERVED_PAYMENT_COUNT)
        end as LATE_PAYMENT_RATE,

        case
            when sum(OBSERVED_PAYMENT_COUNT) = 0 then null
            else
                sum(UNDERPAYMENT_COUNT)::float
                / sum(OBSERVED_PAYMENT_COUNT)
        end as UNDERPAYMENT_RATE,

        avg(AVG_PAYMENT_DELAY_DAYS) as AVG_PAYMENT_DELAY_DAYS

    from credit_repayment

    group by SK_ID_CURR

)

select *
from customer_history