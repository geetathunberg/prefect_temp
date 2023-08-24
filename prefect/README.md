# Deploying and Maintaining Prefect

There's three main services that the repository is deploying to run ELT. 
- dbt
- Prefect
- Airbyte

Prefect is the orchestration tool that performs all the ELT in this repository, including managing Airbyte syncs, and running dbt. 

Airbyte is an ELT tool with community-built connectors for various software/platforms/sources. It makes extracting and loading data from a wide range of sources quick and easy. 

dbt (data build tool) is the T in ELT. dbt transforms data, and is extremely good at it. The dbt project in this repo can be found [here](../dbt).

There are a few hoops to jump through before deploying the stack. 

## GitHub Authentication
First, to always get the latest changes of the dbt project, the production server needs to `git pull` this repository every time the dbt is run. 

The preferred way to do allow git to do that is through setting up a Deploy Key on the repository. Follow [this guide](https://docs.github.com/en/developers/overview/managing-deploy-keys#deploy-keys) to do so.  

Alternatively, it is possible to use a GitHub Token of a user account that is used on the cloud VM. Follow [this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) to obtain the Token. (**Only the `repo` scope is needed.**) 

In this case, this will be the GITHUB_TOKEN variable in the `.env` file (which must be located in the `docker` directory of the project). 

## Accessing the server

The deployed repository should reside on the production server (assuming an instance is already set up and accessible), so it's necessary to connect to it through SSH. 

### Creating a public key and authorizing it on the VM

1. `$ ssh-keygen -t rsa -C "your_email@example.com"` 
2. Copy the contents of `~/.ssh/id_rsa.pub`
3. Connect to the VM through the cloud provider UI, and once in the terminal of the VM, paste the public key into `~/.ssh/authorized_keys` file. 

### Connecting to the server, and port forwarding

You should now be able to connect to the instance on your local machine. In the terminal, 

`$ ssh -L 8000:localhost:8000 -L 8001:localhost:8001 -L 8080:localhost:8080 -L 4200:localhost:4200 -L 4201:localhost:4201 -o LogLevel=quiet ubuntu@IP_ADDRESS`

Where the IP_ADDRESS is the external IP address of the server. 

Note: The forwarding of ports (`8000`, `8001`, `8080`, `4200`, `4201`) allows to access UI's of the services being run on the instance locally. 

## Cloning the repository

After SSH-ing into the server:

1. Open the repository website on GitHub, click the green `Code` button. 
    a. If you have previously set up a Deploy Key on the repository, copy the contents of the SSH tab. It should look like _`git@github.com:TasmanAnalytics/prefect-elt.git`_.

    b. If you are using the Github Token, from the HTTPS tab copy everything after the `@` symbol. It should look like _`@github.com:TasmanAnalytics/prefect-elt.git`_. 

2. Cloning the repo

    a. If you copied the SSH option above, type `$ git clone`, paste the copied git link, and run the command. 

    b. Otherwise, type `$ git clone https://$GITHUB_TOKEN:` then paste the copied piece from above and run the command.  

    - example:  `$ git clone https://$GITHUB_TOKEN:@github.com/TasmanAnalytics/prefect-elt.git/` where $GITHUB_TOKEN is the Token previously obtained, and the rest is the pasted text. 

## Setting up the Environment

Depending on the infrastructure, API's that are being tapped into, and the data warehouse in place, we need to set up appropriate environment variables. 

> Warning: **If Snowflake is used, make sure that the Snowflake account password does not contain a `@` symbol**

### .env file

Finally, `cd` into the repository, create a `.env` file in the `docker` directory, and add the following environment variables. 

1. `$ nano .env`

> Do _not_ add any quotation marks ("") after the (=) sign. 

```bash
# Remove this variable if you have set up a Deploy Key
GITHUB_TOKEN=
# Name of the GitHub organization hosting the repository
GITHUB_ORG_NAME=
# Name of the GitHub repository
GITHUB_REPO_NAME=

# Custom environment variables used in Prefect Flows. 
PREFECT__CONTEXT__SECRETS__CUSTOM_ENV_VAR=
PREFECT__CONTEXT__SECRETS__CUSTOM_ENV_VAR=

PREFECT__CONTEXT__SECRETS__SNOWFLAKE_ACCOUNT=

# Some API Access to Snowflake
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_OPENAPI_USER
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_OPENAPI_PASSWD
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_OPENAPI_ROLE
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_OPENAPI_WAREHOUSE
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_OPENAPI_DATABASE=
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_OPENAPI_SCHEMA=

# dbt Snowflake
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_DBT_USER
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_DBT_PASSWD
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_DBT_ROLE
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_DBT_WAREHOUSE
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_DBT_DATABASE=
PREFECT__CONTEXT__SECRETS__SNOWFLAKE_DBT_SCHEMA=
```
The names of the environment variables need to be present in the [docker/docker-compose.yml](../docker/docker-compose.yml) as well, or otherwise docker will not include them while composing the image. More specifically, they should be under the `services:agent:environment` config. 

Variables that are used within Python scripts in the `prefect` directory must be prefixed with `PREFECT__CONTEXT__SECRETS__`. If they're used within other Shell scripts the prefix is not required. 

If you have set up a Deploy Key, it is required that there is a valid SSH key in the `~/.ssh/` directory on the instance that will be running the jobs. The public key should be deployed in the repository settings on GitHub. Otherwise, make sure to adapt the way the repository is cloned on the instance in the [`setup.sh`](../docker/prefect/setup.sh).

## Deploying the Docker container

Composing the Docker container assumes acting as the `ubuntu` user on the cloud instance.

1. Navigate to the [`<repo_name>/docker`](../docker/) directory
2. To compose the Docker containers, run the follwing in the terminal: `$ docker-compose up -d`

To track logs of the deployment:
1. `$ docker ps`
3. `$ docker logs -f docker_agent_1`
4. Wait until you see some ASCII art of "Prefect Agent" and the logs have halted. At that point you can press `Ctrl+C` to exit the logs. 
5. To access the Prefect UI, open [http://localhost:8080](http://localhost:8080) in a browser. 

## Scheduling Prefect Runs

The way the project is set up, we only schedule a single Flow, which runs all the necessary flows for various tasks (dbt, Airbyte, custom Python extractions). 

1. In the Prefect UI open at [http://localhost:8080](http://localhost:8080), within the Dashboard, open the Flows tab. 

2. Click on the `all-etl` Flow. 

3. In the upper-right corner open Settings, and then the Schedules tab. 

4. Set up a regular flow schedule, or toggle the `Advanced` schedule and make use of the cron job syntax. Within the same `New Schedule` prompt, adjust parameters of the schedule if needed. (If the `all-etl` Flow has no parameters, but the child Flows do, you have to go into the Settings of that specific Flow, and configure its default paramaters. The main `all-etl` Flow will then pick this up when running it. )

5. After clicking `Create`, toggle `SCHEDULE` in the upper-right corner, and wait for the run of the Flow.  

## Investigating Runs

After openning a Flow, under the Runs tab, every Run has Logs that can be inspected. 

## Adding new Flows

To avoid having to compose the Docker containers down when there's updates to the Prefect flows, follow these steps to deploy new/updated Prefect flows. 

1. Navigate to the repository and run `$ git pull`. Note that by doing so, these scripts should also be available in the docker container that you're about to access, because the directory is set up as an external volume for the container. 
2. Navigate to the [`docker`](../docker/) directory
3. To get into the Docker Agent container run `$ docker exec -ti docker_agent_1 /bin/bash`. You are operating on the container. 
4. Get into the directory with Prefect flows: `$ cd ~/flows`
5. To register a flow, run `$ python3 <extract-source>-flow.py`. This Flow is now updated in the Prefect UI. 
