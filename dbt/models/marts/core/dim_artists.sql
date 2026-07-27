{{ config(materialized='table', cluster_by=['artist_id']) }}

with spotify_latest as (
    select
        artist_id,
        artist_name,
        genres,
        popularity,
        external_url
    from {{ ref('stg_spotify__top_artists') }}
    qualify row_number() over (partition by artist_id order by snapshot_date desc) = 1
),

kworb_latest as (
    select
        artist_id,
        artist_name
    from {{ ref('stg_charts__kworb_artist_streams') }}
    qualify row_number() over (partition by artist_id order by snapshot_date desc) = 1
)

select
    coalesce(s.artist_id, k.artist_id) as artist_id,
    coalesce(s.artist_name, k.artist_name) as artist_name,
    s.genres,
    s.popularity,
    s.external_url,
    s.artist_id is not null as in_personal_taste,
    k.artist_id is not null as in_global_chart
from spotify_latest s
full outer join kworb_latest k using (artist_id)
