{{
  config(
    materialized='table',
    partition_by={'field': 'played_at', 'data_type': 'timestamp'},
    cluster_by=['user_id', 'track_id']
  )
}}

select * from {{ ref('stg_spotify__now_playing') }}
