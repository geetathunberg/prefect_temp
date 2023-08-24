{# 

    A frequently used pattern for deduplicating a CTE. 

    Params: 
        - source: cte to deduplicate
        - partition_field: the field in the source to deduplicate on
        - order_field: the timestamp field in the source to order by (allowing to select only one row)
        - order: asc (ascending) or desc (descending) determines if we want to keep the first or the last row

    Usage: 
    final as (
        {{ mcr_source_deduplication(
            'cleaned',
            'event_id',
            'event_timestamp',
            'asc')
        }}
    )

#}

{%
macro
    mcr_source_deduplication (
        source,
        partition_field,
        order_field,
        order
    )
%}
with
ordered as (
    select
        *,
        row_number() over (
            partition by
                {{ partition_field }}
            order by
                {{ order_field }} {{ order }}
        ) as row_number
    from
        {{ source }}
),
deduplicated as (
    select
        *
    from
        ordered
    where
        row_number = 1
)
select * from deduplicated
{% endmacro %}