-- TODO: raw.genre 를 정리하세요. (원본 컬럼: genre_id, name)
-- 힌트: name -> genre_name 으로 바꾸세요.
--
-- 같은 패턴으로 stg_albums.sql, stg_artists.sql 도 작성합니다.

with source as (

    select * from {{ source('chinook_raw', 'genre') }}

)

select
    genre_id,
    name as genre_name
from source
