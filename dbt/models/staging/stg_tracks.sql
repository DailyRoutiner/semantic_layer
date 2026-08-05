-- TODO: raw.track 을 정리하세요.
--
-- 원본 컬럼: track_id, name, album_id, media_type_id, genre_id, composer,
--            milliseconds, bytes, unit_price
--
-- 힌트:
--   - name 은 너무 일반적인 이름입니다. track_name 으로 바꾸세요.
--     (조인했을 때 album.name, genre.name 과 충돌합니다)
--   - milliseconds 는 사람이 못 읽습니다. 파생 컬럼을 만드세요:
--       round(milliseconds / 60000.0, 2) as duration_minutes
--     "재생시간이 긴 곡" 같은 질문이 이 컬럼 하나로 풀립니다.

with source as (

    select * from {{ source('chinook_raw', 'track') }}

),

renamed as (

    select
        track_id, 
        name as track_name,
        album_id,
        media_type_id,
        genre_id, composer,
        round(milliseconds / 60000.0 , 2) as duration_minutes,
        bytes, unit_price

    from source

)

select * from renamed
