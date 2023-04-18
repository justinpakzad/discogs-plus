import sqlalchemy
from sqlalchemy import text
from google.oauth2 import service_account
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import json
import os
from dotenv import load_dotenv
load_dotenv()

credentials_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
    db_user = os.environ["USER_DB"]  # e.g. 'my-db-user'
    db_pass = os.environ["PASSWORD"]  # e.g. 'my-db-password'
    db_name = os.environ["DATABASE_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(credentials=credentials)

    def getconn() -> pg8000.dbapi.Connection:
        LOG.debug("Starting connection attempt")
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool

def make_query(query):
    engine = connect_with_connector()
    query = text(query)
    with engine.connect() as connection:
        result = connection.execute(query).fetchall()
    return result
