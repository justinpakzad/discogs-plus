import discogs_client
import os
from dotenv import load_dotenv
import requests
from db_query import get_artist_track_list
load_dotenv()
user_token = os.getenv("USER_TOKEN")
# artist_tracks = get_artist_track_list()
# rel_ids = [x[0] for x in artist_tracks]
# client = discogs_client.Client(user_agent='justinpakzad/0.1',user_token=user_token)

# have  = []
# want = []
# for id in rel_ids:
#     rel = client.release(id)
#     have.append(client.release(id).fetch('community')['have'])
#     want.append(rel.fetch('community')['want'])

# for h,w in zip(have,want):
#     title_name = [x[1:3]  for x in artist_tracks]
#     print(f"{title_name} has a {w/h} want to have ratio")

haves = []
wants =  []
rel_ids = [5618157,
 6128240,
 3666,
 11761,
 1843494,
 4290966,
 174443,
 4887177,
 943,
 14325184,
 2046211,
 117581]
for id in rel_ids:
    try:
        r  = requests.get(f"https://api.discogs.com/releases/{id}").json()
        haves.append(r['community']['have'])
        wants.append(r['community']['want'])
    except KeyError as e:
        print(f"Error with {e}")



print(haves,wants)
