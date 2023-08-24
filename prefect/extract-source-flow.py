import prefect
from prefect.client.secrets import Secret
from prefect import task, Flow

import os
from sqlalchemy import create_engine
from source_metadata import build_metadata

SNOWFLAKE_USER = Secret('SNOWFLAKE_USER').get()
SNOWFLAKE_PASSWORD = Secret('SNOWFLAKE_PASSWORD').get()
SNOWFLAKE_ACCOUNT = Secret('SNOWFLAKE_ACCOUNT').get()
SNOWFLAKE_ROLE = Secret('SNOWFLAKE_ROLE').get()
SNOWFLAKE_WH = Secret('SNOWFLAKE_WAREHOUSE').get()

# Prefix the Database and Schema names with the extraction name
# e.g. SNOWFLAKE_AIRTABLE_DATABASE, SNOWFLAKE_AIRTABLE_SCHEMA
SNOWFLAKE_DATABASE = Secret('SNOWFLAKE_DATABASE').get()
SNOWFLAKE_SCHEMA = Secret('SNOWFLAKE_SCHEMA').get()

PROJECT_NAME = os.getenv("PREFECT_PROJECT_NAME")

CHUNK_SIZE=10000

logger = prefect.context.get("logger")

def build_database():
    engine = get_engine()
    metadata = build_metadata()
    metadata.create_all(engine)

def get_engine():
    url = "snowflake://{}:{}@{}/{}/{}?warehouse={}&role={}".format(
        SNOWFLAKE_USER,
        SNOWFLAKE_PASSWORD,
        SNOWFLAKE_ACCOUNT,
        SNOWFLAKE_DATABASE,
        SNOWFLAKE_SCHEMA,
        SNOWFLAKE_WH,
        SNOWFLAKE_ROLE
    )

    return create_engine(url)

def divide_chunks(value_list, chunk_size):
    for i in range(0, len(value_list), chunk_size): 
        yield value_list[i:i + chunk_size]

def load_data(table_name, values, chunk_size=CHUNK_SIZE):
    """
    Loads both the messages in their respective tables, and the high water marks in the latest_messages table
    """
    logger = prefect.context.get("logger")

    table_name = f"{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}"
    try:
        engine = get_engine()
        conn = engine.connect()
        ins = build_metadata().tables[table_name].insert()

        logger.info(f"Loading {len(values)} entries into {table_name}.")

        for chunk in divide_chunks(values, chunk_size):
            conn.execute(ins.values(chunk))

    finally:
        conn.close()
        engine.dispose()

@task
def extract_load_objects():
    pass

@task
def setup():
    logger = prefect.context.get("logger")
    logger.info("Initializing database tables if necessary")
    build_database()

with Flow("extract-source") as flow:
    extract_load_objects(
        setup()
    )

flow.register(project_name=PROJECT_NAME, labels=['data-etl'])
