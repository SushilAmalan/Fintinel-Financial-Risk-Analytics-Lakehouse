with applicants as (

    select
        SK_ID_CURR,
        TARGET,

        AMT_INCOME_TOTAL,
        AMT_CREDIT,
        AMT_ANNUITY,
        AMT_GOODS_PRICE,

        EXT_SOURCE_1,
        EXT_SOURCE_2,
        EXT_SOURCE_3

    from {{ ref('stg_application_train') }}

),

repayment as (

    select *
    from {{ ref('int_customer_repayment_history') }}

),

joined as (

    select
        a.SK_ID_CURR,
        a.TARGET,

        a.AMT_INCOME_TOTAL,
        a.AMT_CREDIT,
        a.AMT_ANNUITY,
        a.AMT_GOODS_PRICE,

        a.EXT_SOURCE_1,
        a.EXT_SOURCE_2,
        a.EXT_SOURCE_3,

        case
            when r.SK_ID_CURR is not null then 1
            else 0
        end as HAS_REPAYMENT_HISTORY,

        r.PREVIOUS_CREDIT_COUNT,
        r.TOTAL_INSTALLMENTS,
        r.OBSERVED_PAYMENT_COUNT,
        r.LATE_PAYMENT_COUNT,
        r.UNDERPAYMENT_COUNT,
        r.LATE_PAYMENT_RATE,
        r.UNDERPAYMENT_RATE,
        r.AVG_PAYMENT_DELAY_DAYS,
        r.TOTAL_SCHEDULED_AMOUNT,
        r.TOTAL_PAID_AMOUNT

    from applicants a

    left join repayment r
        on a.SK_ID_CURR = r.SK_ID_CURR

)

select *
from joined