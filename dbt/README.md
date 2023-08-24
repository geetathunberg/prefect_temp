# dbt Project

## Setting up and running dbt

To isolate the Python environment and keep the dbt installation clean, install a virtual environment for this project, and install the necessary dependencies. 

1. Open a terminal and navigate to the dbt directory of the repository. 

2. Assuming Python 3, and the virtualenv* package are already installed, run the following commands:
```!bash
$ python3 -m venv .dbt-venv

# To activate the virtual environment. 
$ source .dbt-venv/bin/activate

# To install Python dependencies.
$ pip3 install -r requirements.txt

# After the work is done, to deactivate the virtual environment. 
$ deactivate
```
> \* If virtualenv is not installed, run the following 2 commands before continuing to Step 2. 
```!bash
$ python3 -m pip install --user --upgrade pip
$ python3 -m pip install --user virtualenv
```

Before being able to run dbt, you need to set up the profile for this project. To do so, edit the `~/.dbt/profiles.yml` file if it exists, and add the necessary config. If it doesn't - create it, and add the config. Documentation on creating your profile for the project can be found [here](https://docs.getdbt.com/dbt-cli/configure-your-profile).
Make sure to set the profile the value set in [`dbt_project.yml`](./dbt_project.yml) under the 'profile_name' variable. 

Once the profile is set up, to test the connection, open the terminal with the virtual environment activated, navigate to the dbt directory, and run `dbt debug`. 

To install necessary dbt dependencies (if there are any), after testing the connection, run `dbt deps`. 

To run the whole dbt project, run `dbt run`. For additional options (running specific models, with a specific target) check out the [dbt docs](https://docs.getdbt.com/reference/commands/run). 

> TODO: Build a shell script that sets up the fully-ready-to-run environment.

## Connecting
For development purposes, you might want to connect to the data warehouse locally, instead of going into its UI. To do that, depending on the data warehouse in place use the appropriate instructions. 

### Connecting to Snowflake
The preferred way to connect to Snowflake is via a username and password. Make sure that you have the appropriate credentials for the Snowflake account that you're aiming to connect to. 

1. Click on the plus on the top left, then Data Source, and choose Snowflake from the dropdown.
2. When prompted to install the Snowflake driver, just go with the flow, install it and wait until it finishes.
3. Give your connection a proper name, something along the lines of `Tasman Snowflake`.
4. Make sure that `Connection type` is 'default'.
5. `Host` should be the full Snowflake Account URL. You can obtain this from the browser, when you go to access Snowflake. Leave the default `Port`. 
6. Enter your credentials, and the wanted Database & Schema. Leave these two empty if you want to access everything that your user has access to. 
7. Choose the appropriate `Warehouse`. 
8. `Test Connection` and once you get a positive response, click `OK`.

### Connecting to BigQuery
The preferred way to connect to a BigQuery project is via a service account. 

1. Obtain the service account JSON key. The safe bet to find the key is to ping the shared channel, tagging people currently developing on the repository. 
2. In addition, in the GCP console, under IAM > Service Accounts, find the email of the service account used for dbt. It should be of the following form: `bigquery-dbt-user@<gcp-project-name>.iam.gserviceaccount.com`. Depending on the SQL IDE being used, follow the corresponding instructions. Any other IDE should be relatively similar to DBeaver and DataGrip. 

#### DataGrip
1. Click on the plus on the top left, then Data Source, and choose BigQuery from the dropdown.
2. When prompted to install the BigQuery driver, just go with the flow, install it and wait until it finishes.
3. Give your connection a proper name, something along the lines of `Tasman BigQuery`.
4. Click on default that’s next to `Connection type`, and select `Service Account`.
5. Leave the default Host.
6. Set `Project` to the name of the GCP project. 
7. Leave `OAuthType` empty.
8. `OAuthServiceAcctEmail` should be `bigquery-dbt-user@<gcp-project-name>.iam.gserviceaccount.com`.
9. `OAuthPvtKeyPath` should be the full path to the JSON key for the service account, that you previously obtained, and stored in a safe place.
10. `Test Connection` and once you get a positive response, click `OK`.

You should see all projects available to the service account in the Database connections panel. To  see specific (or all) schemas and tables, next to the name of the projects, click on the `0 of xx`, select the wanted schemas and give it some time to introspect the databases. 

#### DBeaver

1. Navigate to the `Connect to a database` window. 
2. Make sure that the `Google BigQuery` Driver is installed and selected. 
2. Set `Project` to the name of the GCP project. 
3. If there are any additional projects that dbt should be able to access, add them here. 
4. In `OAuth type` select `Service-based`.
5. `Service` should be `bigquery-dbt-user@<gcp-project-name>.iam.gserviceaccount.com`. 
6. `Key path` should be the full path to the JSON key for the service account, that you previously obtained, and stored in a safe place.
7. Keep the Host and Port default. 
8. Click `Finish`. 

## dbt Cheat Sheet

Taken from [GitHub's dbt cheat sheet](https://about.gitlab.com/handbook/business-technology/data-team/platform/dbt-guide/#command-line-cheat-sheet).

- dbt clean - this will remove the /dbt_modules (populated when you run deps) and /target folder (populated when models are run)
- dbt run - regular run

Model selection syntax (source). Specifying models can save you a lot of time by only running/testing the models that you think are relevant. However, there is a risk that you'll forget to specify an important upstream dependency so it's a good idea to understand the syntax thoroughly:
- dbt run --models modelname - will only run modelname
- dbt run --models +modelname - will run modelname and all parents
- dbt run --models modelname+ - will run modelname and all children
- dbt run --models +modelname+ - will run modelname, and all parents and children
- dbt run --models @modelname - will run modelname, all parents, all children, AND all parents of all children
- dbt run --exclude modelname - will run all models except modelname

Note that all of these work with folder selection syntax too:
- dbt run --models folder - will run all models in a folder
- dbt run --models folder.subfolder - will run all models in the subfolder
- dbt run --models +folder.subfolder - will run all models in the subfolder and all parents
- dbt run --full-refresh - will refresh incremental models
- dbt test - will run custom data tests and schema tests; TIP: dbt test takes the same --model and --exclude syntax referenced for dbt run
- dbt seed - will load csv files specified in the data-paths directory into the data warehouse. 
- dbt compile - compiles all models. This isn't a command you will need to run regularly. dbt will compile the models when you run any models.

Handy shortcuts:
- Run the following command to add the alias for fully refreshing the local dbt environment:
```!bash
$ echo "alias dbt_refresh='dbt clean ; dbt deps ; dbt seed" >> ~/.zshrc
```
After restarting the shell, you'll be able to run `$ dbt_refresh` to run all three commands at once. 
