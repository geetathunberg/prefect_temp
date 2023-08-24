import prefect
from prefect import task, Flow
from prefect.tasks.prefect import StartFlowRun

import os
PROJECT_NAME = os.getenv("PREFECT_PROJECT_NAME")

# Template: Add a StartFlowRun for each source that's in the /prefect_template/prefect/ dir
extract_source = StartFlowRun(flow_name='extract-source', project_name=PROJECT_NAME, wait=True) 

run_dbt = StartFlowRun(flow_name='run-dbt', project_name=PROJECT_NAME, wait=True)

with Flow('all-etl') as flow:
    # Template: Add all upstream tasks from above
    run_dbt(upstream_tasks=[extract_source]) 

flow.register(project_name=PROJECT_NAME, labels=['data-etl']) 