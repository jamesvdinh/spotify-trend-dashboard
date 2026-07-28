with source as (
    select * from {{ source('spotify_raw', 'spotify_now_playing_events') }}
),

deduped as (
    select
        *,
        row_number() over (
            partition by user_id, track_id, played_at
            order by loaded_at desc
        ) as rn
    from source
)

select
    user_id,
    track_id,
    track_name,
    artist_names,
    album_image_url,
    is_playing,
    progress_ms,
    duration_ms,
    played_at,
    context_uri,
    polled_at,
    loaded_at
from deduped
where rn = 1
