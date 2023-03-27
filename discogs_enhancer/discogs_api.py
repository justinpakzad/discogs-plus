import discogs_client
import os
from dotenv import load_dotenv
import requests

load_dotenv()
user_token = os.getenv("USER_TOKEN")


client = discogs_client.Client(user_agent='justinpakzad/0.1',user_token=user_token)
