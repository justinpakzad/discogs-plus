import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

# conn_pool = psycopg2.pool.ThreadedConnectionPool(
#     1, 20,
#     host=os.environ.get('HOST'),
#     dbname=os.environ.get('DATABASE_NAME'),
#     user=os.environ.get('USER_DB'),
#     password=os.environ.get('PASSWORD'),
#     port=os.environ.get('PORT')
# )
