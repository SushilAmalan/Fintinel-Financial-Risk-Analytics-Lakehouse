with payment_events as (

    select *
    from {{ ref('int_installment_payment_events') }}

),

aggregated as (

    select
        SK_ID_PREV,
        SK_ID_CURR,

        count(*) as TOTAL_INSTALLMENTS,

        count(DAYS_ENTRY_PAYMENT) as OBSERVED_PAYMENT_COUNT,

        sum(
            case
                when IS_LATE_PAYMENT = 1 then 1
                else 0
            end
        ) as LATE_PAYMENT_COUNT,

        sum(
            case
                when IS_UNDERPAYMENT = 1 then 1
                else 0
            end
        ) as UNDERPAYMENT_COUNT,

        sum(AMT_INSTALMENT) as TOTAL_SCHEDULED_AMOUNT,
        sum(AMT_PAYMENT) as TOTAL_PAID_AMOUNT,

        avg(PAYMENT_DELAY_DAYS) as AVG_PAYMENT_DELAY_DAYS,

        avg(
            case
                when IS_LATE_PAYMENT is not null
                    then IS_LATE_PAYMENT
            end
        ) as LATE_PAYMENT_RATE,

        avg(
            case
                when IS_UNDERPAYMENT is not null
                    then IS_UNDERPAYMENT
            end
        ) as UNDERPAYMENT_RATE

    from payment_events

    group by
        SK_ID_PREV,
        SK_ID_CURR

)

select *
from aggregated