import json
import pandas as pd

import psycopg2
import os
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

conn = connect_database()
cur = conn.cursor()
def make_collection_df():
    query1 = 'SELECT id,username, unnest(collection_ids) AS release_id FROM user_collection;'
    collection_df = pd.read_sql_query(query1, conn)
    collection_df['score'] = 2
    return collection_df

def make_wantlist_df()
    query2= 'SELECT id,username, unnest(wantlist_ids) AS release_id FROM user_wantlist;'
    wantlist_df = pd.read_sql_query(query2, conn)
    wantlist_df['score'] = 1
    return wantlist_df

cur.close()
conn.close()

merged_df = pd.concat([collection_df, wantlist_df], ignore_index=True)
merged_df = merged_df.rename(columns={'id':'user_id'})

print(f"We have {len(merged_df['username'].unique())} unique users")
print(f"We have {len(merged_df['release_id'].unique())} unique releases")


