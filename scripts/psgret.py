import psycopg2
import os
import csv
import bz2
import sys

import time
conn = psycopg2.connect(
    host="localhost",
    dbname="Discogs_Data",
    user="postgres",
    password="nhlnhl2",
    port="5432"
)

cur = conn.cursor()

query = """
SELECT
    release_artist.artist_id,
    release_artist.artist_name,
    release.title
FROM
    release
    JOIN release_style ON release.id = release_style.release_id
    JOIN release_format ON release.id = release_format.release_id
    JOIN release_genre ON release.id = release_genre.release_id
    JOIN release_artist ON release.id = release_artist.release_id
WHERE
    master_id IS NULL
    AND genre = 'Electronic'
    AND style LIKE ANY (ARRAY['%Electro%', '%Tech House%','%Techno%'])
    AND country LIKE ANY (ARRAY['%USA%', '%US%'])
    AND name = 'Vinyl'
    AND release_year BETWEEN 1988 AND 2010
	AND release_artist.artist_id IN(
	SELECT release_artist.artist_id
	FROM release_artist
	GROUP BY release_artist.artist_id
	HAVING COUNT(*) = 1
	)



"""
start = time.time()
cur.execute(query)
results = cur.fetchall()
cur.close()
conn.close()
print(results)
end = time.time()
print(f"It took {end-start} and there are {(len(results))} releases in your search")
print('\n')
print(results)
