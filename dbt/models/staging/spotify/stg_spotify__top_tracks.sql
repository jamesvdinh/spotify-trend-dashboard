with source as (
    select * from {{ source('spotify_raw', 'spotify_top_tracks_snapshot') }}
),

deduped as (
    select
        *,
        row_number() over (
            partition by user_id, time_range, snapshot_date, track_id
            order by loaded_at desc
        ) as rn
    from source
)

select
    user_id,
    time_range,
    snapshot_date,
    rank,
    track_id,
    json_value(track_json, '$.name') as track_name,
    json_value(track_json, '$.external_urls.spotify') as external_url,
    cast(json_value(track_json, '$.duration_ms') as int64) as duration_ms,
    cast(json_value(track_json, '$.popularity') as int64) as popularity,
    (
        select string_agg(json_value(artist, '$.name'), ', ')
        from unnest(json_query_array(track_json, '$.artists')) as artist
    ) as artist_names,
    loaded_at
from deduped
where rn = 1
