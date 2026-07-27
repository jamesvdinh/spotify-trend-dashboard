{#
  Default dbt-bigquery behavior concatenates custom schema onto the target
  schema (e.g. `staging_marts`). We already provisioned a plain `marts`
  dataset by hand, so use the custom schema name literally instead.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
