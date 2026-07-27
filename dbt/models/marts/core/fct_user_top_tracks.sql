{{
  config(
    materialized='table',
    partition_by={'field': 'snapshot_date', 'data_type': 'date'},
    cluster_by=['user_id', 'track_id']
  )
}}

select * from {{ ref('stg_spotify__top_tracks') }}
