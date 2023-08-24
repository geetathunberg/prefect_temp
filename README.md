# ETL Prefect Project

[Instructions on setting up the infrastructure on an instance.](./prefect/README.md)

[Instructions on setting up and running dbt locally.](./dbt/README.md)

## Infrastructure in Place

> Placeholder for documenting what has been deployed. (Or a URL of that doc)

### CI Workflow

In the [.github/workflows](.github/workflows) directory, a GitHub action that protects the `main` branch from unreviewed PRs and standalone commits. It also runs dbt to make sure that the PR has not caused any braking changes. 
