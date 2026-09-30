with source as (

    select *
    from {{ source('raw', 'installments_payments') }}

),

renamed as (

    select
        SK_ID_PREV,
        SK_ID_CURR,
        NUM_INSTALMENT_VERSION,
        NUM_INSTALMENT_NUMBER,
        DAYS_INSTALMENT,
        DAYS_ENTRY_PAYMENT,
        AMT_INSTALMENT,
        AMT_PAYMENT

    from source

)

select *
from renamed