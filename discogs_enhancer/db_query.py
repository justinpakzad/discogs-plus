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
        host=os.getenv('HOST'),
        dbname=os.getenv('DATABASE_NAME'),
        user=os.getenv('USER_DB'),
        password=os.getenv('PASSWORD'),
        port=os.getenv('PORT')
    )
    return conn

def get_artist_track_list(
    genre="Electronic",
    style=["%Electro%","%Tech House%"],
    country="US",
    format="Vinyl",
    start_year=1989,
    end_year=1996,
    limit=50):

    conn = connect_database()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT DISTINCT
            ra.artist_name,
            r.title,
            rv.uri
        FROM
            release r
            JOIN release_style AS rs ON r.id = rs.release_id
            JOIN release_format AS rf ON r.id = rf.release_id
            JOIN release_genre AS rg ON r.id = rg.release_id
            JOIN release_artist AS ra ON r.id = ra.release_id
            JOIN release_video AS rv ON r.id = rv.release_id
        WHERE
            r.master_id IS NULL
            AND rg.genre = '{genre}'
            AND rs.style LIKE ANY (ARRAY{style})
            AND r.country = '{country}'
            AND rf.name = '{format}'
            AND r.release_year BETWEEN {start_year} AND {end_year}
        LIMIT {limit}
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()
    artist_track_url_list = [(artist,track,uri) for artist,track,uri in results]
    return artist_track_url_list
