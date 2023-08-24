use role SYSADMIN;
-- Create Warehouses
--   Compute WH
create warehouse if not exists COMPUTE_WH with warehouse_size = 'XSMALL' auto_suspend = 5 auto_resume = TRUE initially_suspended = TRUE;
create warehouse if not exists ETL_WH with warehouse_size = 'XSMALL' auto_suspend = 5 auto_resume = TRUE initially_suspended = TRUE;
create warehouse if not exists DEV_DBT_WH with warehouse_size = 'XSMALL' auto_suspend = 5 auto_resume = TRUE initially_suspended = TRUE;
create warehouse if not exists PROD_DBT_WH with warehouse_size = 'XSMALL' auto_suspend = 5 auto_resume = TRUE initially_suspended = TRUE;
create warehouse if not exists BI_WH with warehouse_size = 'XSMALL' auto_suspend = 5 auto_resume = TRUE initially_suspended = TRUE;

-- ------------------------
use role SYSADMIN;
-- Create Databases
--   Source databases
create database if not exists SOURCE_AIRBYTE;
--   Database for Prefect Tasks
create database if not exists SOURCE_SYNC;
--   Analytics (dbt) database
create database if not exists ANALYTICS;

-- ------------------------
use role SECURITYADMIN;
-- Create Roles
--   DBA Role
create role if not exists DBA;
grant role SECURITYADMIN to role DBA;
grant role SYSADMIN to role DBA;
grant role DBA to role ACCOUNTADMIN;
grant monitor usage on account to role DBA;
grant imported privileges on database snowflake to role DBA;

--   Tasman Roles
create role if not exists TASMAN_DEV_ROLE;
create role if not exists TASMAN_VIEWER_ROLE;
grant role TASMAN_DEV_ROLE to role SYSADMIN;
grant role TASMAN_VIEWER_ROLE to role TASMAN_DEV_ROLE;

--   Client Roles
create role if not exists DEV_ROLE;
create role if not exists VIEWER_ROLE;
grant role DEV_ROLE to role SYSADMIN;
grant role VIEWER_ROLE to role DEV_ROLE;

--   Application Roles
create role if not exists APPLICATION_ROLE;
create role if not exists AIRBYTE_ROLE;
create role if not exists BI_ROLE;
grant role APPLICATION_ROLE to role SYSADMIN;
grant role BI_ROLE to role APPLICATION_ROLE;
grant role AIRBYTE_ROLE to role APPLICATION_ROLE;

--   Production Roles
create role if not exists PROD_ROLE;
create role if not exists PROD_DBT_ROLE;
create role if not exists PROD_ETL_ROLE;
grant role PROD_ROLE to SYSADMIN;
grant role PROD_DBT_ROLE to role PROD_ROLE;
grant role PROD_ETL_ROLE] to role PROD_ROLE;

use role SECURITYADMIN;
-- Grant Privileges
-- TODO: Work out the grants to objects for all roles

-- ------------------------
use role USERADMIN;
-- Create Users
create user if not exists TASMAN_NAME_LASTNAME password = '' login_name = 'TASMAN_NAME_LASTNAME' first_name = 'Jovan' last_name = 'Sakovic' email = 'jovan@tasman.ai' default_role = "TASMAN_DEV_ROLE" must_change_password = TRUE;
grant role TASMAN_DEV_ROLE to user TASMAN_NAME_LASTNAME;

create user if not exists LOOKER_USER password = '' login_name = 'LOOKER_USER' default_role = 'BI_ROLE' must_change_password = FALSE;
grant role BI_ROLE to user LOOKER_USER;
create user if not exists METABASE_USER password = '' login_name = 'METABASE_USER' default_role = 'BI_ROLE' must_change_password = FALSE;
grant role BI_ROLE to user METABASE_USER;
create user if not exists AIRBYTE_USER password = '' login_name = 'AIRBYTE_USER' default_role = 'AIRBYTE_ROLE' must_change_password = FALSE;
grant role AIRBYTE_ROLE to user AIRBYTE_USER;
