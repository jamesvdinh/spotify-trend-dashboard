{{
  config(
    materialized='table',
    partition_by={'field': 'snapshot_date', 'data_type': 'date'},
    cluster_by=['user_id', 'artist_id']
  )
}}

-- How the user's top artists stack up against global chart velocity on the
-- same day. Inner join is intentional: an artist only shows up here if they
-- appear in both the user's top artists AND that day's global leaderboard -
-- niche artists the user listens to that never chart globally are expected
-- to be absent, not a bug.
select
    personal.user_id,
    personal.time_range,
    personal.snapshot_date,
    personal.artist_id,
    personal.artist_name,
    personal.rank as personal_rank,
    global.rank as global_rank,
    global.rank_change_7d as global_rank_change_7d,
    global.daily_streams_millions as global_daily_streams_millions
from {{ ref('fct_user_top_artists') }} as personal
inner join {{ ref('fct_artist_velocity') }} as global
    on personal.artist_id = global.artist_id
    and personal.snapshot_date = global.snapshot_date
