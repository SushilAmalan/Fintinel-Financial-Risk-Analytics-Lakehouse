with source as (

    select *
    from {{ source('raw', 'previous_application') }}

),

renamed as (

    select
        SK_ID_PREV,
        SK_ID_CURR,

        NAME_CONTRACT_TYPE,
        NAME_CONTRACT_STATUS,

        AMT_ANNUITY,
        AMT_APPLICATION,
        AMT_CREDIT,
        AMT_DOWN_PAYMENT,
        AMT_GOODS_PRICE,

        RATE_DOWN_PAYMENT,
        RATE_INTEREST_PRIMARY,
        RATE_INTEREST_PRIVILEGED,

        NAME_CASH_LOAN_PURPOSE,
        NAME_PAYMENT_TYPE,
        CODE_REJECT_REASON,
        NAME_CLIENT_TYPE,
        NAME_GOODS_CATEGORY,
        NAME_PORTFOLIO,
        NAME_PRODUCT_TYPE,
        CHANNEL_TYPE,

        CNT_PAYMENT,

        NAME_YIELD_GROUP,
        PRODUCT_COMBINATION,

        DAYS_DECISION,
        DAYS_FIRST_DRAWING,
        DAYS_FIRST_DUE,
        DAYS_LAST_DUE_1ST_VERSION,
        DAYS_LAST_DUE,
        DAYS_TERMINATION,

        NFLAG_INSURED_ON_APPROVAL

    from source

)

select *
from renamed