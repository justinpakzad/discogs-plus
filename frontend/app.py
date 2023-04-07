from flask import Flask,render_template,request,redirect,url_for
import psycopg2
import os
from psycopg2 import Error
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




def search_tracks(conn,genre,formatz,style,year_from,year_to,countries,one_release=False,no_master=False):
    cursor = conn.cursor()
    style = style.split(',') if style else ''
    countries = countries.split(',') if countries else ''
    print(f'genre: {genre}')
    print(f'format: {formatz}')
    print(f'style: {style}')
    print(f'year_from: {year_from}')
    print(f'year_to: {year_to}')
    print(f'countries: {countries}')
    q = """SELECT DISTINCT
		ra.artist_name,
		r.title,
        random() as rand
    FROM
        release r
        JOIN release_style AS rs ON r.id = rs.release_id
        JOIN release_format AS rf ON r.id = rf.release_id
        JOIN release_genre AS rg ON r.id = rg.release_id
        JOIN release_artist AS ra ON r.id = ra.release_id
        JOIN release_video AS rv ON r.id = rv.release_id
    WHERE
        rg.genre = %s
        AND rf.name = (%s)
        AND rs.style LIKE ANY(%s)
        AND r.release_year BETWEEN %s AND %s
        AND r.country LIKE ANY(%s)
    ORDER BY rand
    LIMIT 10"""

    if no_master:
        q += 'AND r.master_id IS NULL'
    if one_release:
        q += """AND ra.artist_name IN (
		SELECT ra2.artist_name
		FROM release_artist ra2
		GROUP BY ra2.artist_name
		HAVING COUNT(ra2.release_id) = 1
	)"""
    cursor.execute(q,(genre, formatz, style, year_from, year_to, countries))
    results = cursor.fetchall()
    return results




app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/search", methods=["POST"])
def search():
    print(request.get_data())
    genre = request.form.get('genre')
    style = request.form.get('style')
    countries = request.form.get('countries')
    formatz = request.form.get('format')
    year_from = request.form.get('year_from')
    year_to = request.form.get('year_to')
    one_release = request.form.get('one_release') == 'on'
    no_master = request.form.get('no_master') == 'on'
    connection = connect_database()
    if connection:
        tracks = search_tracks(connection,genre,formatz,style,year_from,year_to,countries,one_release,no_master)
        connection.close()
        return render_template("results.html", tracks=tracks)
    else:
        return "Unable to connect to the database."


if __name__ == "__main__":
    app.run(debug=True)
