import psycopg2
import os
import csv
import bz2
import sys
import time
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def connect_database():
    conn = psycopg2.connect(
        host="localhost",
        dbname="Discogs_Data",
        user="postgres",
        password=os.getenv('PASSWORD'),
        port="5432"
    )
    return conn

def get_artist_track_list(
    genre="Electronic",
    style=["%Electro%"],
    country=["%UK%"],
    format="Vinyl",
    start_year=1991,
    end_year=1996,
    limit=10):

    conn = connect_database()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT DISTINCT
            ra.artist_name,
            r.title
        FROM
            release r
            JOIN release_style rs ON r.id = rs.release_id
            JOIN release_format rf ON r.id = rf.release_id
            JOIN release_genre rg ON r.id = rg.release_id
            JOIN release_artist ra ON r.id = ra.release_id
        WHERE
            r.master_id IS NULL
            AND rg.genre = '{genre}'
            AND rs.style LIKE ANY (ARRAY{style})
            AND r.country LIKE ANY (ARRAY{country})
            AND rf.name = '{format}'
            AND r.release_year BETWEEN {start_year} AND {end_year}

        LIMIT {limit}
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()
    artist_track_list = [(artist,track) for artist,track in results]
    return artist_track_list

x  = get_artist_track_list()
print(x)
