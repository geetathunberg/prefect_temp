
{#

    A frequently used pattern for generating schema names is to change the behavior based on dbt environment, such that:

    In prod:

    - If a custom schema is provided, a model schema name should match the custom schema, rather than being concatenated to the target schema.
    If no custom schema is provided, a model schema name should match the target schema.

    In other environments (e.g. dev or qa):

    - Build all models in the target schema, as in, ignore custom schema configurations.
    dbt ships with a global macro that contains this logic – generate_schema_name_for_env.

#}

{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ generate_schema_name_for_env(custom_schema_name, node) }}
{%- endmacro %}