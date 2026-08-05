-- TODO: raw.artist (artist_id, name) -> artist_name 으로 이름 정리

with source as (

    select * from {{ source('chinook_raw', 'artist') }}

)

select
    artist_id,
    name as artist_name 
from source
