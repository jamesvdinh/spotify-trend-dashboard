{{
  config(
    materialized='table',
    partition_by={'field': 'session_start_at', 'data_type': 'timestamp'},
    cluster_by=['user_id']
  )
}}

-- Groups consecutive now-playing events into listening sessions: a new
-- session starts whenever the gap since the user's previous track exceeds
-- SESSION_GAP_MINUTES (long enough that it's a new sitting, not a pause).
{% set session_gap_minutes = 30 %}

with events as (
    select *
    from {{ ref('fct_now_playing_events') }}
    where is_playing
),

with_gaps as (
    select
        *,
        timestamp_diff(
            played_at,
            lag(played_at) over (partition by user_id order by played_at),
            minute
        ) as minutes_since_previous_track
    from events
),

with_session_numbers as (
    select
        *,
        sum(
            case
                when minutes_since_previous_track is null
                    or minutes_since_previous_track > {{ session_gap_minutes }}
                then 1
                else 0
            end
        ) over (partition by user_id order by played_at) as session_number
    from with_gaps
)

select
    user_id,
    session_number,
    min(played_at) as session_start_at,
    max(played_at) as session_end_at,
    timestamp_diff(max(played_at), min(played_at), second) as session_duration_seconds,
    count(distinct track_id) as unique_track_count,
    count(*) as track_play_count
from with_session_numbers
group by user_id, session_number
