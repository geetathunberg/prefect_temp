#!/bin/bash

# Add prerequisite debian packages
apt update
apt install -y git

# Set git SSH key
echo $GIT_PRIVATE_KEY | tr ";" "\n" > /root/.ssh/id_ed25519
chmod 600 /root/.ssh/id_ed25519

# Clone repo for running dbt
git clone ${GIT_USER}@${GIT_HOST}:${GIT_ORG_NAME}/${GIT_REPO_NAME}.git /root/data-etl

# Add prerequisite python packages
pip3 install --upgrade pip
pip3 install --upgrade -r /root/prefect/requirements.txt
pip3 install --force-reinstall MarkupSafe==2.0.1

# Set up prefect and add flows
cp /root/prefect/config.toml /root/.prefect/config.toml

prefect server create-tenant --name "Client Name" --slug clientslug
prefect create project ${PREFECT_PROJECT_NAME}

# Register all Prefect flows in the flows directory
find /root/flows -name \*-flow.py | xargs -n 1 python3

# Start prefect agent
prefect agent local start --label data-etl --import-path /root/flows
