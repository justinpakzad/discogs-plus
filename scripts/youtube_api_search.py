from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
from db_query import get_artist_track_list
import re
load_dotenv()

api_key = os.getenv('YOTUBE_API_KEY')
service_name = os.getenv('YOUTUBE_API_SERVICE_NAME')
version = os.getenv('YOUTUBE_API_VERSION')
youtube = build(service_name,version,developerKey=api_key)


artist_track_list = get_artist_track_list()


def search_video(artist_name,trackname):
    youtube = build(service_name,version,developerKey=api_key)
    response = youtube.search().list(
        q=f"{artist_name} {trackname}",
        type='video',
        part='id'
    ).execute()
    video_id = response['items'][0]['id']['videoId']
    return video_id




def get_video_ids():
    batch_size = 10
    video_ids = []
    for i in range(0,len(artist_track_list),batch_size):
        batch = artist_track_list[i:i+batch_size]
        for artist,track in batch:
            video_ids.append(search_video(artist,track))
    return video_ids
