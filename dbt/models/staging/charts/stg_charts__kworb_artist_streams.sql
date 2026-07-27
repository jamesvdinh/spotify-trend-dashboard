with source as (
    select * from {{ source('kworb_raw', 'kworb_artist_streams_snapshot') }}
),

deduped as (
    select
        *,
        row_number() over (
            partition by snapshot_date, artist_id
            order by loaded_at desc
        ) as rn
    from source
)

select
    snapshot_date,
    rank,
    artist_id,
    artist_name,
    total_streams_millions,
    daily_streams_millions,
    streams_lead_millions,
    streams_solo_millions,
    streams_featured_millions,
    loaded_at
from deduped
where rn = 1
