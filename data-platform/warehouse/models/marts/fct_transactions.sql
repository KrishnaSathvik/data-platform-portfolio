{{ config(materialized='table') }}

select
    transaction_id,
    user_id,
    amount,
    merchant,
    transaction_timestamp,
    is_fraud,
    payment_method,
    location,
    case 
        when amount > 500 then 'high'
        when amount > 100 then 'medium'
        else 'low'
    end as amount_category,
    extract(hour from transaction_timestamp) as transaction_hour
from {{ ref('stg_transactions') }}
