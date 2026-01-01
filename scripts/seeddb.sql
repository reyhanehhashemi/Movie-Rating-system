-- =====================================================================
-- Seed TMDB 5000 Dataset into movies_db
-- Adapted to project schema:
--   - genres_movie (join table)
--   - movie_ratings(created_at) instead of rated_at
--   - movies without description column
-- =====================================================================

-------------------------- 1. Clean previous staging tables --------------------------
DROP TABLE IF EXISTS tmdb_movies_raw CASCADE;
DROP TABLE IF EXISTS tmdb_credits_raw CASCADE;
DROP TABLE IF EXISTS tmdb_selected CASCADE;

-------------------------- 2. Create staging tables --------------------------
-- tmdb_5000_movies.csv
CREATE TABLE tmdb_movies_raw (
    budget NUMERIC,
    genres JSONB,
    homepage TEXT,
    id INTEGER PRIMARY KEY,
    keywords JSONB,
    original_language TEXT,
    original_title TEXT,
    overview TEXT,
    popularity NUMERIC,
    production_companies JSONB,
    production_countries JSONB,
    release_date TEXT,
    revenue NUMERIC,
    runtime NUMERIC,
    spoken_languages JSONB,
    status TEXT,
    tagline TEXT,
    title TEXT,
    vote_average NUMERIC,
    vote_count INTEGER
);

-- tmdb_5000_credits.csv
CREATE TABLE tmdb_credits_raw (
    movie_id INTEGER,
    title TEXT,
    "cast" JSONB,
    crew JSONB
);

-------------------------- 3. Load CSVs into staging --------------------------
-- توجه: این مسیرها نسبت به جایی که psql را اجرا می‌کنید هستند.
-- اگر از روت پروژه این اسکریپت را بزنید، همین مسیرها صحیح‌اند.
\copy tmdb_movies_raw  FROM 'scripts/tmdb_5000_movies.csv'   WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
\copy tmdb_credits_raw FROM 'scripts/tmdb_5000_credits.csv'  WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-------------------------- 4. Build tmdb_selected (top 1000 movies) --------------------------
CREATE TABLE tmdb_selected AS
WITH joined AS (
    SELECT
        m.id              AS tmdb_id,
        m.title           AS title,
        m.genres          AS genres,
        m.release_date    AS release_date,
        m.vote_average    AS vote_average,
        m.vote_count      AS vote_count,
        m.popularity      AS popularity,
        c."cast"            AS "cast",
        (
            SELECT c_el->>'name'
            FROM jsonb_array_elements(c.crew::jsonb) AS c_el
            WHERE c_el->>'job' = 'Director'
              AND c_el->>'name' IS NOT NULL
            ORDER BY c_el->>'name'
            LIMIT 1
        ) AS director_name
    FROM tmdb_movies_raw m
    JOIN tmdb_credits_raw c
      ON m.id = c.movie_id
)
SELECT *
FROM (
    SELECT
        j.*,
        ROW_NUMBER() OVER (
            ORDER BY
                j.vote_count   DESC NULLS LAST,
                j.popularity   DESC NULLS LAST,
                j.vote_average DESC NULLS LAST,
                j.tmdb_id      ASC
        ) AS rn
    FROM joined j
) AS ranked
WHERE rn <= 1000;

-------------------------- 5. Insert genres (real data from TMDB) --------------------------
INSERT INTO genres (name, description)
SELECT DISTINCT
    trim(g->>'name') AS name,
    'Imported from TMDB genres' AS description
FROM tmdb_movies_raw m,
     LATERAL jsonb_array_elements(m.genres::jsonb) AS g
WHERE g->>'name' IS NOT NULL
ORDER BY 1;

-------------------------- 6. Insert directors --------------------------
INSERT INTO directors (name, birth_year, description)
SELECT DISTINCT
    ts.director_name AS name,
    NULL::INT        AS birth_year,
    'Imported from TMDB 5000 dataset (no birth year available)' AS description
FROM tmdb_selected ts
WHERE ts.director_name IS NOT NULL
ORDER BY 1;

-------------------------- 7. Insert movies (1000 films) --------------------------
-- توجه: جدول movies ستون‌های created_at و updated_at را دارد و NOT NULL هستند،
-- پس باید آن‌ها را هم با NOW() مقداردهی کنیم.
INSERT INTO movies (title, director_id, release_year, "cast", created_at, updated_at)
SELECT
    s.title,
    d.id AS director_id,
    COALESCE(
        NULLIF(split_part(s.release_date, '-', 1), '')::INT,
        2000
    ) AS release_year,
    (
        SELECT string_agg(cn, ', ')
        FROM (
            SELECT (c_el->>'name') AS cn
            FROM jsonb_array_elements(s."cast"::jsonb) AS c_el
            WHERE c_el->>'name' IS NOT NULL
            ORDER BY COALESCE((c_el->>'order')::INT, 999999)
            LIMIT 3
        ) AS sub
    ) AS cast_string,
    NOW() AS created_at,
    NOW() AS updated_at
FROM tmdb_selected s
JOIN directors d
  ON d.name = s.director_name
ORDER BY s.tmdb_id;


-------------------------- 8. Insert movie–genre relations into genres_movie --------------------------
-- این بخش ژانرهای هر فیلم را به جدول join شما (genres_movie) منتقل می‌کند.
WITH movie_map AS (
    SELECT
        s.tmdb_id,
        m.id AS movie_id
    FROM tmdb_selected s
    JOIN movies m
      ON m.title = s.title
)
INSERT INTO genres_movie (movie_id, genre_id)
SELECT DISTINCT
    mm.movie_id,
    g.id AS genre_id
FROM tmdb_movies_raw m
JOIN movie_map mm
  ON mm.tmdb_id = m.id
CROSS JOIN LATERAL jsonb_array_elements(m.genres::jsonb) AS g_json
JOIN genres g
  ON g.name = trim(g_json->>'name')
WHERE g_json->>'name' IS NOT NULL;

-------------------------- 9. Insert random ratings (simulated user scores) --------------------------
-- توجه: در اسکیما‌ی شما ستون زمان در movie_ratings نامش created_at است.
-- برای هر فیلم، تعدادی امتیاز تصادفی (۱ تا ۱۰) در پنج سال گذشته ثبت می‌کنیم.
INSERT INTO movie_ratings (movie_id, score, created_at)
SELECT
    m.id AS movie_id,
    (floor(random() * 10) + 1)::INT AS score,
    now() - (random() * interval '5 years') AS created_at
FROM movies m
CROSS JOIN generate_series(1, 5) AS g(n)   -- تا ۵ امتیاز برای هر فیلم
WHERE random() < 0.7;                      -- حدوداً ۷۰٪ فیلم‌ها امتیاز می‌گیرند

-- =====================================================================
-- End of seed script
-- =====================================================================
