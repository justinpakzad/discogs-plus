import discogs_client
import os
from dotenv import load_dotenv
import requests
from db_query import get_artist_track_list

load_dotenv()
user_token = os.getenv("USER_TOKEN")

# client = discogs_client.Client(user_agent='justinpakzad/0.1',user_token=user_token)
headers = {
    "User-Agent": "YourApplication/1.0",
    "Authorization": f"Discogs token={user_token}",
}


def search_release(start_year: int, end_year: int, style: str) -> dict:
    obscurity_threshold = 0.7
    max_haves = 250
    max_wants = 100
    for year in range(start_year, end_year + 1):
        page = 1
        while True:
            data = requests.get(
                f"https://api.discogs.com/database/search?genre=electronic&style={style}&year={year}&page={page}&format=vinyl&country=UK&type=release",
                headers=headers,
            ).json()
            if data.get("results"):
                for results in data["results"]:
                    songs = results["title"]
                    want = results["community"]["want"]
                    have = results["community"]["have"]
                    links = f"https://www.discogs.com{results['uri']}"
                    if have <= max_haves and want <= max_wants:
                        with open('discogs.txt','a') as f:
                            f.write(links +'\n')

            else:
                break

            page += 1


releases = search_release(2001, 2010, "tech house")
