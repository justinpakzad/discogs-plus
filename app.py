from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2 import Error, pool
import time
import random
from dotenv import load_dotenv
import logging
import json
import re
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "discogs_plus"))
from discogs_plus.youtube_api_search import get_ids_regex
from discogs_plus.make_playlist import make_playlist, add_songs_to_playlist, authenticate_youtube
load_dotenv()
import requests
from style_genres import genres,styles,country,formats



# conn_pool = psycopg2.pool.ThreadedConnectionPool(
#     1, 20,
#     host=os.environ.get('HOST'),
#     dbname=os.environ.get('DATABASE_NAME'),
#     user=os.environ.get('USER_DB'),
#     password=os.environ.get('PASSWORD'),
#     port=os.environ.get('PORT')
# )


def search_tracks(conn, genre, formatz, style, year_from, year_to, countries, one_release=False, no_master=False,limit_results=False):
    cursor = conn.cursor()
    style = ['%' + s.strip() + '%' for s in style.split(',')] if style else ['%']
    countries = [c.strip() for c in countries.split(',')] if countries else ['%']
    formatz = [f.strip() for f in formatz.split(',')]  if formatz else ['%']
    limit_clause = "LIMIT 120" if limit_results else ""

    one_release_condition = f"AND filtered_drd.artist_release_count = 1" if one_release else ""

    no_master_condition = f"AND r.master_id IS NULL" if no_master else ""

    q = f"""
    WITH filtered_drd AS (
    SELECT *,
        COUNT(*) OVER (PARTITION BY artist_name) as artist_release_count
    FROM trimmed_denormalized_release_data
    WHERE
        genre = %s
        AND format LIKE ANY(%s)
        AND release_year BETWEEN %s AND %s
        AND country LIKE ANY(%s)
    )
    SELECT DISTINCT ON (filtered_drd.artist_name)
        r.id as release_id,
        filtered_drd.artist_name,
        r.title,
        filtered_drd.label_name,
        filtered_drd.release_year,
        filtered_drd.country,
        rv.uri
    FROM
        release_trimmed r
    JOIN release_video_trimmed AS rv ON r.id = rv.release_id
    JOIN release_artist_trimmed ra ON r.id = ra.release_id
    JOIN filtered_drd ON r.title = filtered_drd.title AND ra.artist_name = filtered_drd.artist_name
    WHERE
        ra.role = ''
        AND EXISTS (
            SELECT 1
            FROM unnest(%s) AS s
            WHERE filtered_drd.style LIKE s
        )
        {one_release_condition}
        {no_master_condition}
    ORDER BY filtered_drd.artist_name, filtered_drd.release_year, r.title, filtered_drd.country
    {limit_clause}
    """

    cursor.execute(q, (genre, formatz, year_from, year_to, countries, style))
    results = cursor.fetchall()
    tracks = [{'release_id': release_id, 'artist': artist, 'title': title, 'label': label, 'year': release_year, 'country': country,'video':video} for
              release_id, artist, title, label, release_year, country,video in results]
    return tracks

def validate_input(g,s,c,f):
    valid_genre = genres
    valid_styles = styles
    valid_countries = country
    valid_format  = formats

    if g  != 'Electronic':
        return False

    if ',' in s:
        s_list = s.split(',')
        for styl in s_list:
            if styl not in valid_styles:
                return False
    elif s not in valid_styles:
            return False

    if ',' in c:
        c_list = c.split(',')
        for ct in c_list:
            if ct not in valid_countries:
                return False
    elif c not in valid_countries:
        return False

    if ',' in f:
        f_list = f.split(',')
        for form in f_list:
            if form not in valid_format:
                return False
    elif f not in valid_format:
        return False
    return True

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_params = request.form.to_dict()
        return redirect(url_for('search', **search_params))

    genre = request.args.get('genre')
    style = request.args.get('style')
    countries = request.args.get('countries')
    search_format = request.args.get('format')
    year_from = request.args.get('year_from')
    year_to = request.args.get('year_to')
    one_release = request.args.get('one_release') == 'on'
    no_master = request.args.get('no_master') == 'on'
    gen_playlist = request.args.get('generate_playlist') == 'on'
    playlist_name = request.args.get('playlist_name')
    playlist_description = request.args.get('playlist_description')
    page = int(request.args.get('page', 1))
    if any(x is None or x.strip() == '' for x in [genre, style, countries, search_format, year_from, year_to]):
        return redirect(url_for('home'))

    if not validate_input(genre, style, countries, search_format):
        return redirect(url_for('home'))

    connection = conn_pool.getconn()

    if connection:
        try:
            search_start = time.time()
            tracks = search_tracks(connection, genre, search_format, style, year_from, year_to, countries, one_release, no_master,limit_results=gen_playlist)
            search_end = time.time()
            if gen_playlist:
                playlist_start = time.time()
                links = [t['video'] for t in tracks]
                vid_ids = get_ids_regex(links)
                authenticate_youtube()
                playlist_id = make_playlist(playlist_name, playlist_description)
                add_songs_to_playlist(playlist_id, vid_ids)
                playlist_end = time.time()
                print(f"Normal search took {search_end - search_start:.2f} seconds")
                print(f"Creating playlist took {playlist_end - playlist_start:.2f} seconds")
                return render_template('home.html')
            else:
                print(f"Normal search took {search_end - search_start:.2f} seconds")
                return render_template("results.html", tracks=tracks, page=page, genre=genre, style=style, countries=countries, format=search_format, year_from=year_from, year_to=year_to, one_release=one_release, no_master=no_master)
        except Exception as e:
            pass
        finally:
            conn_pool.putconn(connection)

if __name__ == '__main__':
    app.run(debug=True)
