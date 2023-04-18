import os
import json
from google.oauth2 import service_account
from google.cloud.sql.connector import connector
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    credentials_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    credentials_dict = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)

    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    db_user = os.environ["USER_DB"]
    db_pass = os.environ["PASSWORD"]
    db_name = os.environ["DATABASE_NAME"]

    conn = connector.connect(
        instance_connection_name,
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name,
        credentials=credentials
    )
    return conn

connection = create_connection()
