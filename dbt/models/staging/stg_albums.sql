-- TODO: raw.album (album_id, title, artist_id) -> album_title 로 이름 정리

with source as (

    select * from {{ source('chinook_raw', 'album') }}

)

select
    album_id,
    title as album_title,
    artist_id
from source
