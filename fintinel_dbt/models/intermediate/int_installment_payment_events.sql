with payments as (

    select
        SK_ID_PREV,
        SK_ID_CURR,
        NUM_INSTALMENT_VERSION,
        NUM_INSTALMENT_NUMBER,
        DAYS_INSTALMENT,
        DAYS_ENTRY_PAYMENT,
        AMT_INSTALMENT,
        AMT_PAYMENT

    from {{ ref('stg_installments_payments') }}

),

derived as (

    select
        *,

        case
            when DAYS_ENTRY_PAYMENT is null
              or DAYS_INSTALMENT is null
                then null
            when DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT
                then 1
            else 0
        end as IS_LATE_PAYMENT,

        case
            when AMT_PAYMENT is null
              or AMT_INSTALMENT is null
                then null
            when AMT_PAYMENT < AMT_INSTALMENT
                then 1
            else 0
        end as IS_UNDERPAYMENT,

        case
            when DAYS_ENTRY_PAYMENT is null
              or DAYS_INSTALMENT is null
                then null
            else DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT
        end as PAYMENT_DELAY_DAYS,

        case
            when AMT_PAYMENT is null
              or AMT_INSTALMENT is null
                then null
            else AMT_INSTALMENT - AMT_PAYMENT
        end as PAYMENT_SHORTFALL_AMOUNT

    from payments

)

select *
from derived