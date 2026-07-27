{{
  config(
    materialized='table',
    partition_by={'field': 'snapshot_date', 'data_type': 'date'},
    cluster_by=['artist_id']
  )
}}

-- Rank/streams change over a trailing 7-day window. Needs at least 7 days of
-- daily snapshots accumulated before rank_change_7d stops being null.
with source as (
    select * from {{ ref('stg_charts__kworb_artist_streams') }}
),

with_lag as (
    select
        *,
        lag(rank, 7) over (partition by artist_id order by snapshot_date) as rank_7d_ago,
        lag(daily_streams_millions, 7) over (partition by artist_id order by snapshot_date)
            as daily_streams_millions_7d_ago
    from source
)

select
    snapshot_date,
    artist_id,
    artist_name,
    rank,
    rank_7d_ago,
    rank_7d_ago - rank as rank_change_7d,  -- positive = rising (lower rank number is better)
    daily_streams_millions,
    daily_streams_millions_7d_ago,
    daily_streams_millions - daily_streams_millions_7d_ago as daily_streams_change_7d
from with_lag
