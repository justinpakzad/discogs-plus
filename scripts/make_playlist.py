from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from  google.auth.transport.requests import Request
import re
import os
from youtube_api_search import get_video_ids
load_dotenv()

flow = InstalledAppFlow.from_client_secrets_file('scripts/client_secret_946485639839-1beknq37id68h379c16gejsamj68ban8.apps.googleusercontent.com.json',
                                                scopes=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.upload',
                                                        'https://www.googleapis.com/auth/youtubepartner'],redirect_uri='http://localhost:8080/')

flow.run_local_server(port=8080,authorization_prompt_message='')

credentials = flow.credentials

youtube = build('youtube','v3',credentials=credentials)


def make_playlist(title, description):
    response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    ).execute()
    playlist_id = response["id"]
    return playlist_id


def add_songs_to_playlist(playlist_id, video_ids):
    for video_id in video_ids:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
playlist_id = make_playlist('Testing101','')

video_ids = get_video_ids()

add_songs_to_playlist(playlist_id,video_ids)
