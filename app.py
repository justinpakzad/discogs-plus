import sys
import os
from database import create_connection
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template, request, redirect, url_for
from flask.logging import create_logger
import logging
from dotenv import load_dotenv  # Add this line
from search import search_tracks,validate_input
from playlist import create_playlist
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

    if not validate_input(search_params["genre"], search_params["style"], search_params["countries"], search_params["search_format"]):
        return redirect(url_for('home'))

    connection = create_connection()

    if connection:
        try:
            gen_playlist = search_params.pop("gen_playlist")  # Remove 'gen_playlist' from search_params
            playlist_name = search_params.pop("playlist_name")  # Remove 'playlist_name' from search_params
            playlist_description = search_params.pop("playlist_description")  # Remove 'playlist_description' from search_params

            tracks = search_tracks(connection, **search_params)
            if gen_playlist:
                create_playlist(tracks, playlist_name, playlist_description)
                return render_template('home.html')
            else:
                return render_template("results.html", tracks=tracks, **search_params)
        except Exception as e:
            LOG.error(f"An error occurred while searching tracks: {e}")
            return f"An error occurred while searching tracks: {e}", 500
        finally:
            connection.close()
    else:
        LOG.error("No connection available")
        return "No connection available", 500

if __name__ == '__main__':
    app.run(debug=True)
