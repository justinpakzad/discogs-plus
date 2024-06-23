import os
import json
from google.oauth2 import service_account
from google.cloud.sql.connector import Connector
import pg8000
from dotenv import load_dotenv
import psycopg2
load_dotenv()

# def create_cloud_connection() -> pg8000.dbapi.Connection:
#     credentials_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
#     credentials_dict = json.loads(credentials_json)
#     credentials = service_account.Credentials.from_service_account_info(credentials_dict)

#     instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
#     db_user = os.environ["USER_DB"]
#     db_pass = os.environ["PASSWORD"]
#     db_name = os.environ["DATABASE_NAME"]
#     connector = Connector(credentials=credentials)

#     conn: pg8000.dbapi.Connection = connector.connect(
#         instance_connection_name,
#         "pg8000",
#         user=db_user,
#         password=db_pass,
#         db=db_name
#     )
#     return conn

def create_local_connection():
    conn = psycopg2.connect(
        host=os.getenv('LOCALHOST'),
        dbname=os.getenv('DATABASE_NAME'),
        user=os.getenv('USER_DB'),
        password=os.getenv('LOCALPASSWORD'),
        port=os.getenv('PORT')
    )
    return conn

conn = create_local_connection()

