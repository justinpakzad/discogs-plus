import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "discogs_plus"))
from discogs_plus.youtube_api_search import get_ids_regex
from discogs_plus.make_playlist import make_playlist, add_songs_to_playlist, authenticate_youtube
import time



def create_playlist(tracks, playlist_name, playlist_description):
    playlist_start = time.time()
    links = [t['video'] for t in tracks]
    vid_ids = get_ids_regex(links)
    authenticate_youtube()
    playlist_id = make_playlist(playlist_name, playlist_description)
    add_songs_to_playlist(playlist_id, vid_ids)
    playlist_end = time.time()
    print(f"Creating playlist took {playlist_end - playlist_start:.2f} seconds")
