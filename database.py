import psycopg2
from psycopg2.pool import ThreadedConnectionPool

import os
from dotenv import load_dotenv

load_dotenv()

conn_pool = ThreadedConnectionPool(
    1, 20,
    os.environ.get('HOST'),
    os.environ.get('DATABASE_NAME'),
    os.environ.get('USER_DB'),
    os.environ.get('PASSWORD'),
    os.environ.get('PORT')
)
