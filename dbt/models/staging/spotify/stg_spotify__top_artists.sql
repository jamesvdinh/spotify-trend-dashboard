with source as (
    select * from {{ source('spotify_raw', 'spotify_top_artists_snapshot') }}
),

deduped as (
    select
        *,
        row_number() over (
            partition by user_id, time_range, snapshot_date, artist_id
            order by loaded_at desc
        ) as rn
    from source
)

select
    user_id,
    time_range,
    snapshot_date,
    rank,
    artist_id,
    json_value(artist_json, '$.name') as artist_name,
    json_value(artist_json, '$.external_urls.spotify') as external_url,
    cast(json_value(artist_json, '$.popularity') as int64) as popularity,
    (
        select array_agg(json_value(genre))
        from unnest(json_query_array(artist_json, '$.genres')) as genre
    ) as genres,
    loaded_at
from deduped
where rn = 1
