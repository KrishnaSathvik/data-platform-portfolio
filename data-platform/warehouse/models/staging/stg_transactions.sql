{{ config(materialized='view') }}

select
    transaction_id,
    user_id,
    amount,
    merchant,
    timestamp::timestamp as transaction_timestamp,
    is_fraud,
    payment_method,
    location,
    device_id
from {{ source('raw', 'transactions') }}
where transaction_id is not null
