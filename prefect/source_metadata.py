from prefect.client.secrets import Secret

from sqlalchemy import MetaData, Table, Column
from sqlalchemy.types import *

# Prefix the Database and Schema names with the extraction name
# e.g. SNOWFLAKE_AIRTABLE_DATABASE, SNOWFLAKE_AIRTABLE_SCHEMA
SNOWFLAKE_DATABASE = Secret('SNOWFLAKE_DATABASE').get()
SNOWFLAKE_SCHEMA = Secret('SNOWFLAKE_SCHEMA').get()

def build_metadata():
    metadata = MetaData(schema=f'{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}')

    Table('table_name', metadata,
        Column('column_name', BOOLEAN()),
        Column('column_name', VARCHAR(length=16777216)),
        Column('column_name', TIMESTAMP(timezone=True)),
    ), 

    Table('other_table_name', metadata,
        Column('column_name', BOOLEAN()),
        Column('column_name', BOOLEAN()),
        Column('column_name', BOOLEAN()),
    )
    
    return metadata