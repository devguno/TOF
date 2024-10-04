WITH procedure_stats AS (
    SELECT 
        procedure_source_value,
        COUNT(*) as count,
        MIN(procedure_date) as earliest_date,
        MAX(procedure_date) as latest_date
    FROM 
        cdm2024.procedure_occurrence
    WHERE 
        procedure_source_value IN (
            'RM2103', 'RM21211', 'RM21211C', 'RM21212', 'RM21212C',
            'RM2121C', 'HCSRM213', 'HCSRM0002', 'HCSRM2131C', 'HCSRM217',
            'RM2101', 'RM2101C', 'RM213', 'RM2131C', 'RM218C', 'RM2111C', 
            'RM21111C', 'RM2106'
        )
    GROUP BY 
        procedure_source_value
),
total_count AS (
    SELECT 
        SUM(count) as total,
        MIN(earliest_date) as overall_earliest_date,
        MAX(latest_date) as overall_latest_date
    FROM procedure_stats
),
result_set AS (
    SELECT 
        ps.procedure_source_value,
        ps.count,
        tc.total,
        CAST(ROUND(CAST(ps.count AS NUMERIC) / CAST(tc.total AS NUMERIC) * 100, 2) AS NUMERIC(5,2)) AS percentage,
        ps.earliest_date,
        ps.latest_date,
        0 AS sort_order
    FROM 
        procedure_stats ps
    CROSS JOIN 
        total_count tc
    UNION ALL
    SELECT 
        'Total' as procedure_source_value,
        tc.total as count,
        tc.total,
        100.00 AS percentage,
        tc.overall_earliest_date as earliest_date,
        tc.overall_latest_date as latest_date,
        1 AS sort_order
    FROM 
        total_count tc
)
SELECT 
    procedure_source_value,
    count,
    total,
    percentage,
    earliest_date,
    latest_date
FROM 
    result_set
ORDER BY 
    sort_order,
    count DESC;
    


SELECT po.*
FROM cdm2024.procedure_occurrence po
INNER JOIN public.vdtof_cohort vc ON po.person_id = vc.person_id
WHERE po.procedure_source_value IN (
    'RM2103', 'RM21211', 'RM21211C', 'RM21212', 'RM21212C',
    'RM2121C', 'HCSRM213', 'HCSRM0002', 'HCSRM2131C', 'HCSRM217',
    'RM2101', 'RM2101C', 'RM213', 'RM2131C', 'RM218C', 'RM2111C',
    'RM21111C', 'RM2106'
);



WITH procedure_stats AS (
    SELECT
        procedure_source_value,
        COUNT(*) as count,
        MIN(procedure_date) as earliest_date,
        MAX(procedure_date) as latest_date
    FROM
        cdm2024.procedure_occurrence
    WHERE
        procedure_source_value IN (
            'RM2103', 'RM21211', 'RM21211C', 'RM21212', 'RM21212C',
            'RM2121C', 'HCSRM213', 'HCSRM0002', 'HCSRM2131C', 'HCSRM217',
            'RM2101', 'RM2101C', 'RM213', 'RM2131C', 'RM218C', 'RM2111C',
            'RM21111C', 'RM2106'
        )
        AND person_id IN (SELECT person_id FROM public.vdtof_cohort)
    GROUP BY
        procedure_source_value
),
total_count AS (
    SELECT
        SUM(count) as total
    FROM procedure_stats
),
result_set AS (
    SELECT
        ps.procedure_source_value,
        ps.count,
        tc.total,
        CAST(ROUND(CAST(ps.count AS NUMERIC) / CAST(tc.total AS NUMERIC) * 100, 2) AS NUMERIC(5,2)) AS percentage,
        ps.earliest_date,
        ps.latest_date,
        0 AS sort_order
    FROM
        procedure_stats ps
    CROSS JOIN
        total_count tc
    UNION ALL
    SELECT
        'Total' as procedure_source_value,
        SUM(ps.count) as count,
        tc.total,
        100.00 AS percentage,
        MIN(ps.earliest_date) as earliest_date,
        MAX(ps.latest_date) as latest_date,
        1 AS sort_order
    FROM
        procedure_stats ps
    CROSS JOIN
        total_count tc
    GROUP BY
        tc.total
)
SELECT
    procedure_source_value,
    count,
    total,
    percentage,
    earliest_date,
    latest_date
FROM
    result_set
ORDER BY
    sort_order,
    count DESC;
    
   
WITH procedure_stats AS (
    SELECT
        procedure_source_code,
        COUNT(*) as count,
        MIN(procedure_datetime) as earliest_date,
        MAX(procedure_datetime) as latest_date
    FROM
        public.vdtof_mri
    WHERE
        procedure_source_code IN (
            'RM2103', 'RM21211', 'RM21211C', 'RM21212', 'RM21212C',
            'RM2121C', 'HCSRM213', 'HCSRM0002', 'HCSRM2131C', 'HCSRM217',
            'RM2101', 'RM2101C', 'RM213', 'RM2131C', 'RM218C', 'RM2111C',
            'RM21111C', 'RM2106'
        )
    GROUP BY
        procedure_source_code
),
total_count AS (
    SELECT
        SUM(count) as total
    FROM procedure_stats
),
result_set AS (
    SELECT
        ps.procedure_source_code,
        ps.count,
        tc.total,
        CAST(ROUND(CAST(ps.count AS NUMERIC) / CAST(tc.total AS NUMERIC) * 100, 2) AS NUMERIC(5,2)) AS percentage,
        ps.earliest_date,
        ps.latest_date,
        0 AS sort_order
    FROM
        procedure_stats ps
    CROSS JOIN
        total_count tc
    UNION ALL
    SELECT
        'Total' as procedure_source_code,
        SUM(ps.count) as count,
        tc.total,
        100.00 AS percentage,
        MIN(ps.earliest_date) as earliest_date,
        MAX(ps.latest_date) as latest_date,
        1 AS sort_order
    FROM
        procedure_stats ps
    CROSS JOIN
        total_count tc
    GROUP BY
        tc.total
)
SELECT
    procedure_source_code,
    count,
    total,
    percentage,
    earliest_date,
    latest_date
FROM
    result_set
ORDER BY
    sort_order,
    count DESC;