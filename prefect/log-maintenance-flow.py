import prefect
from prefect import task, Flow, Parameter
from prefect.client import Secret
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, MetaData, Table, Column, delete
from sqlalchemy.types import *

logger = prefect.context.get("logger")

POSTGRES_PREFECT_PORT = Secret("POSTGRES_PREFECT_PORT").get()
POSTGRES_PREFECT_USER = Secret("POSTGRES_PREFECT_USER").get()
POSTGRES_PREFECT_PASSWD = Secret("POSTGRES_PREFECT_PASSWD").get()
POSTGRES_PREFECT_HOST = Secret("POSTGRES_PREFECT_HOST").get()
POSTGRES_PREFECT_DATABASE = Secret("POSTGRES_PREFECT_DATABASE").get()

def build_metadata():
    metadata = MetaData()

    Table('log', metadata,
        Column('flow_run_id', VARCHAR(length=16777216)),
        Column('tenant_id', VARCHAR(length=16777216)),
        Column('task_run_id', VARCHAR(length=16777216)),
        Column('timestamp', TIMESTAMP(timezone=True)),
        Column('name', VARCHAR(length=16777216)),
        Column('level', VARCHAR(length=16777216)),
        Column('message', VARCHAR(length=16777216)),
        Column('info', JSON),
        Column('id', VARCHAR(length=16777216)),
        Column('created', TIMESTAMP(timezone=True)),
        Column('updated', TIMESTAMP(timezone=True)),
        Column('is_loaded_from_archive', BOOLEAN),
    )

    return metadata

def get_engine():
    url = "postgresql://{}:{}@{}:{}/{}".format(
        POSTGRES_PREFECT_USER,
        POSTGRES_PREFECT_PASSWD,
        POSTGRES_PREFECT_HOST,
        POSTGRES_PREFECT_PORT,
        POSTGRES_PREFECT_DATABASE
    )
    return create_engine(url)

@task
def get_historic_time(microseconds, seconds, minutes,
                    hours, days, weeks, months, years):

    params = [microseconds, seconds, minutes, hours, days, weeks, months, years]
    # Safety Measure: if no parameters have been set? Nothing will be deleted
    if all([param == 0 for param in params]):
        return False
    
    else:
        now = datetime.now()
        time = now + relativedelta(microseconds=-microseconds, 
                                   seconds=-seconds, 
                                   minutes=-minutes, 
                                   hours=-hours, 
                                   days=-days, 
                                   weeks=-weeks, 
                                   months=-months, 
                                   years=-years
                                )
        logger.info(f"Task 'get_historic_time': Setting to delete logs before: {time}")
        return time

@task
def drop_old_logs(log_time):

    if log_time:
        engine = get_engine()
        conn = engine.connect()

        table = build_metadata().tables["log"]
        statement = delete(table).where(table.c.timestamp <= log_time)

        conn.execute(statement)
        
        logger.info(f"Task 'drop_old_logs': Logs before {log_time} successfully deleted")
        conn.close()
    
    else:
        logger.info("Task 'drop_old_logs': A parameter needs to be set before this task can delete anything")
        
with Flow("log-maintenance-flow") as flow:

    microseconds = Parameter("microseconds", default=0)
    seconds      = Parameter("seconds", default=0)
    minutes      = Parameter("minutes", default=0)
    hours        = Parameter("hours", default=0)
    days         = Parameter("days", default=0)
    weeks        = Parameter("weeks", default=0)
    months       = Parameter("months", default=0)
    years        = Parameter("years", default=0)

    log_time = get_historic_time(microseconds, seconds, minutes,
                               hours, days, weeks, months, years)

    drop_old_logs(log_time)

flow.register(project_name="Tasman", labels=['data-etl'])
