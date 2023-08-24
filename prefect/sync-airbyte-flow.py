import prefect
from prefect import Flow, Parameter, task
from prefect.tasks.airbyte.airbyte import AirbyteConnectionTask
from datetime import timedelta

@task
def sync_airbyte(connections, logger):

    logger.info(f"connections: {connections}")

    for connection_id in connections:
        logger.info(f"Syncing connection: {connection_id}")
        airbyte_sync = AirbyteConnectionTask(
            max_retries=3, 
            retry_delay=timedelta(seconds=10),
            airbyte_server_host="airbyte-server",
            airbyte_server_port="8001",
            airbyte_api_version="v1",
            connection_id=connection_id,
        ).run()

with Flow("sync-airbyte") as flow:
    logger = prefect.context.get("logger")

    connections = Parameter('connections', default=[])
    sync_airbyte(connections, logger)

flow.register(project_name='Tasman', labels=['data-etl'])