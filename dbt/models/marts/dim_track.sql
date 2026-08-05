-- TODO: 곡 차원 테이블. 한 행 = 곡 1개.
--
-- 이 모델이 이 프로젝트의 핵심 아이디어를 보여줍니다.
-- 프로젝트 1에서 LLM은 "장르별 판매량"을 구하려고 매번 이렇게 짰습니다:
--
--     InvoiceLine -> Track -> Genre   (3중 조인, 다리 테이블 Track 을 스스로 찾아야 함)
--
-- 여기서 genre_name 을 미리 붙여두면 그 조인이 통째로 사라집니다.
--
-- 필요한 컬럼:
--   track_id, track_name, duration_minutes, unit_price,
--   album_id, album_title, artist_id, artist_name, genre_id, genre_name
--
-- 힌트:
--   with tracks as (select * from {{ ref('stg_tracks') }}),
--        albums as (select * from {{ ref('stg_albums') }}),
--        ...
--   - 조인은 전부 left join 으로 하세요. 장르가 없는 곡이 실제로 존재합니다.
--   - 장르/앨범이 null 인 경우 coalesce(genre_name, '(미분류)') 를 고려하세요.
--     LLM이 null 처리를 잊는 것보다 여기서 정하는 게 안전합니다.

with track as(
    select * from {{ ref('stg_tracks')}}
),
albums as (
    select * from {{ ref('stg_albums')}}
),
genre as (
    select * from {{ ref('stg_genres')}}
),
artist as (
    select * from {{ ref('stg_artists')}}
)
select a.track_id, a.track_name, a.duration_minutes, a.unit_price,
    b.album_id, b.album_title, d.artist_id, d.artist_name, c.genre_id, 
    coalesce(c.genre_name, '미분류') as genre_name
from track a
    left join albums b using (album_id)
    left join genre c using (genre_id)
    left join artist d using (artist_id)