from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from  google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.errors
import json
import re
import os
import sys
from youtube_api_search import get_ids_regex
load_dotenv()


youtube = None

from google.oauth2.credentials import Credentials


def get_tokens():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"  # For command-line use

    oauth_scopes = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtubepartner",
    ]

    flow = InstalledAppFlow.from_client_info(
        client_config={
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
            }
        },
        scopes=oauth_scopes,
    )

    credentials = flow.run_local_server(port=0)
    return credentials.access_token, credentials.refresh_token


def authenticate_youtube():
    global youtube

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    access_token = os.environ.get("YOUTUBE_ACCESS_TOKEN")

    credentials = Credentials.from_authorized_user_info(
        info={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "access_token": access_token
        },
        scopes=["https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtubepartner"]
    )

    youtube = build("youtube", "v3", credentials=credentials)



def make_playlist(title, description):
    response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "unlisted"
            }
        }
    ).execute()
    playlist_id = response["id"]
    return playlist_id

def check_playlist_items(playlist_id,video_ids):
    existing_ids = set()
    page_token = None
    while True:
        playlist_items = youtube.playlistItems().list(
            playlistId=playlist_id,
            part="contentDetails",
            maxResults=50,
            pageToken=page_token
        ).execute()
        for item in playlist_items["items"]:
            video_id = item["contentDetails"]["videoId"]
            existing_ids.add(video_id)
        page_token = playlist_items.get("nextPageToken")

        if not page_token:
            break
    return [video_id for video_id in video_ids if video_id not in existing_ids]


def add_songs_to_playlist(playlist_id, video_ids):
    for video_id in video_ids:
        video_obj = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body=video_obj
            ).execute()
        except googleapiclient.errors.HttpError as e:
            error_json = json.loads(e.content)
            if error_json["error"]["errors"][0]["reason"] == "videoNotFound":
                print(f"Video with ID {video_id} not found.")
            else:
                print(f"Error adding video {video_id} to playlist: {e}")
