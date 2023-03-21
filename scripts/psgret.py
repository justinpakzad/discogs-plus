import psycopg2
import os
import csv
import bz2
import sys
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
DISTINCT
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
    AND style = 'Electro'
	AND name = 'Vinyl'
    AND release_year BETWEEN 1988 AND 1995

"""

cur.execute(query)
results = cur.fetchall()
cur.close()
conn.close()
print(results)


print(len(results))
