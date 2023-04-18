import sys
import os
import time
import sqlalchemy
from sqlalchemy import text
from google.oauth2 import service_account
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template, request, redirect, url_for,jsonify
from flask.logging import create_logger
import logging
import psycopg2  # Add this line
from dotenv import load_dotenv  # Add this line
import json
# from database import conn_pool
# from search import search_tracks, validate_input
# from playlist import create_playlist
load_dotenv()
app = Flask(__name__)
LOG = create_logger(app)

logging.basicConfig(level=logging.DEBUG)
LOG.setLevel(logging.DEBUG)

# Testing
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


credentials_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
    db_user = os.environ["USER_DB"]  # e.g. 'my-db-user'
    db_pass = os.environ["PASSWORD"]  # e.g. 'my-db-password'
    db_name = os.environ["DATABASE_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(credentials=credentials)

    def getconn() -> pg8000.dbapi.Connection:
        LOG.debug("Starting connection attempt")
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool

    # connection = None
    # LOG.debug("Starting connection attempt")
    # start_time = time.time()
    # try:
    #     LOG.debug(os.environ.get('HOST'))
    #     LOG.debug(os.environ.get('DATABASE_NAME'))
    #     LOG.debug(os.environ.get('USER_DB'))
    #     LOG.debug(os.environ.get('PASSWORD'))
    #     LOG.debug(os.environ.get('DB_PORT'))
    #     connection = psycopg2.connect(
    #     host=os.environ.get('HOST'),
    #     dbname=os.environ.get('DATABASE_NAME'),
    #     user=os.environ.get('USER_DB'),
    #     password=os.environ.get('PASSWORD'),
    #     port=os.environ.get('DB_PORT', '5432'))
    #     if connection:
    #         end_time = time.time()
    #         LOG.debug(f"Connection successful, time elapsed: {end_time - start_time} seconds")
    #         return "Connection to the database is successful!"
    # except Exception as exce:
    #     end_time = time.time()
    #     LOG.error(f"An error occurred while connecting to the database: {exce}, time elapsed: {end_time - start_time} seconds")
    #     return f"An error occurred while connecting to the database: {exce}", 500
    # finally:
    #     if connection:
    #         connection.close()

@app.route("/test_db")
def test_connection():
    engine = connect_with_connector()
    query = text("SELECT * FROM release_artist_trimmed LIMIT 5")
    with engine.connect() as connection:
        result = connection.execute(query)
        rows = [row._mapping for row in result]
    return jsonify(rows)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_params = request.form.to_dict()
        return redirect(url_for('search', **search_params))

    search_params = {
        "genre": request.args.get('genre'),
        "style": request.args.get('style'),
        "countries": request.args.get('countries'),
        "search_format": request.args.get('format'),
        "year_from": request.args.get('year_from'),
        "year_to": request.args.get('year_to'),
        "one_release": request.args.get('one_release') == 'on',
        "limit_results": request.args.get('generate_playlist') == 'on',
        "no_master": request.args.get('no_master') == 'on',
        "gen_playlist": request.args.get('generate_playlist') == 'on',
        "playlist_name": request.args.get('playlist_name'),
        "playlist_description": request.args.get('playlist_description'),
    }

    if any(x is None or x.strip() == '' for x in [search_params["genre"], search_params["style"], search_params["countries"], search_params["search_format"], search_params["year_from"], search_params["year_to"]]):
        return redirect(url_for('home'))

    # if not validate_input(search_params["genre"], search_params["style"], search_params["countries"], search_params["search_format"]):
    #     return redirect(url_for('home'))

    # connection = conn_pool.getconn()

    # if connection:
    #     try:
    #         gen_playlist = search_params.pop("gen_playlist")  # Remove 'gen_playlist' from search_params
    #         playlist_name = search_params.pop("playlist_name")  # Remove 'playlist_name' from search_params
    #         playlist_description = search_params.pop("playlist_description")  # Remove 'playlist_description' from search_params

    #         tracks = search_tracks(connection, **search_params)
    #         if gen_playlist:
    #             create_playlist(tracks, playlist_name, playlist_description)
    #             return render_template('home.html')
    #         else:
    #             return render_template("results.html", tracks=tracks, **search_params)
    #     except Exception as e:
    #         app.logger.error(f"An error occurred while searching tracks: {e}")
    #         return f"An error occurred while searching tracks: {e}", 500
    #     finally:
    #         conn_pool.putconn(connection)
    # else:
    #     app.logger.error("No connection available")
    #     return "No connection available", 500

if __name__ == '__main__':
    app.run(debug=True)
