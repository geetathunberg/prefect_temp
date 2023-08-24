import prefect
from prefect import task, Flow
from prefect.tasks.shell import ShellTask
from prefect.tasks.dbt import DbtShellTask
from prefect.tasks.gcp.secretmanager import GCPSecret

# Data Warehouse credentials stored in a Doppler environment
SNOWFLAKE_ACCOUNT=GCPSecret('SNOWFLAKE_ACCOUNT').get()
SNOWFLAKE_USER=GCPSecret('SNOWFLAKE_USER').get()
SNOWFLAKE_PASSWORD=GCPSecret('SNOWFLAKE_PASSWORD').get()
SNOWFLAKE_ROLE=GCPSecret('SNOWFLAKE_ROLE').get()
SNOWFLAKE_DATABASE=GCPSecret('SNOWFLAKE_DBT_DATABASE').get()
SNOWFLAKE_SCHEMA=GCPSecret('SNOWFLAKE_DBT_SCHEMA').get()
SNOWFLAKE_WAREHOUSE=GCPSecret('SNOWFLAKE_WAREHOUSE').get()

logger = prefect.context.get("logger")

shell = ShellTask(helper_script="cd /root/data-etl")

dbt = DbtShellTask(
    profile_name='client_snowflake',
    environment='prod',
    dbt_kwargs={
        'type': 'snowflake',
        'account': SNOWFLAKE_ACCOUNT,
        'user': SNOWFLAKE_USER,
        'password': SNOWFLAKE_PASSWORD,
        'role': SNOWFLAKE_ROLE,
        'warehouse': SNOWFLAKE_WAREHOUSE,
        'database': SNOWFLAKE_DATABASE,
        'schema': SNOWFLAKE_SCHEMA,
        'threads': 8
    },
    helper_script="cd /root/data-etl/dbt",
    overwrite_profiles=True,
    return_all=True,
    log_stderr=True
)

with Flow('run-dbt') as flow:
    git_pull = shell(command="git pull")
    dbt_deps = dbt(command="dbt deps", upstream_tasks=[git_pull])
    dbt_seed = dbt(command="dbt seed", upstream_tasks=[dbt_deps])
    dbt_run = dbt(command="dbt run", upstream_tasks=[dbt_seed])

flow.register(project_name='Tasman', labels=['data-etl'])
