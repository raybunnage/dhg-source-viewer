-- Function to analyze potential unique constraints
CREATE OR REPLACE FUNCTION analyze_unique_constraints(p_table_name text)
RETURNS TABLE (
    column_name text,
    distinct_ratio numeric,
    recommendation text
) AS $$
BEGIN
    RETURN QUERY
    WITH column_stats AS (
        SELECT 
            a.attname,
            pg_stats.n_distinct,
            pg_stats.null_frac,
            (SELECT count(*) FROM ONLY pg_catalog.pg_class c WHERE c.relname = p_table_name) as total_rows
        FROM pg_attribute a
        JOIN pg_class t ON a.attrelid = t.oid
        LEFT JOIN pg_stats ON t.relname = pg_stats.tablename AND a.attname = pg_stats.attname
        WHERE t.relname = p_table_name AND a.attnum > 0 AND NOT a.attisdropped
    )
    SELECT 
        attname,
        CASE 
            WHEN n_distinct < 0 THEN abs(n_distinct)
            WHEN n_distinct > 0 THEN n_distinct / total_rows::numeric
            ELSE 0
        END as distinct_ratio,
        CASE 
            WHEN n_distinct < 0 AND abs(n_distinct) > 0.95 THEN 'Highly recommended for UNIQUE constraint'
            WHEN n_distinct > 0 AND (n_distinct / total_rows::numeric) > 0.95 THEN 'Consider UNIQUE constraint'
            ELSE 'Not recommended for UNIQUE constraint'
        END as recommendation
    FROM column_stats;
END;
$$ LANGUAGE plpgsql;

-- Function to analyze potential foreign key relationships
CREATE OR REPLACE FUNCTION analyze_foreign_keys(p_table_name text)
RETURNS TABLE (
    column_name text,
    potential_reference_table text,
    potential_reference_column text,
    match_percentage numeric
) AS $$
BEGIN
    RETURN QUERY
    WITH column_values AS (
        SELECT 
            a.attname as column_name,
            t2.relname as ref_table,
            a2.attname as ref_column,
            count(distinct c1.value) as distinct_values,
            count(distinct c2.value) as matching_values
        FROM pg_attribute a
        JOIN pg_class t ON a.attrelid = t.oid
        CROSS JOIN pg_class t2
        JOIN pg_attribute a2 ON a2.attrelid = t2.oid
        LEFT JOIN LATERAL (
            SELECT DISTINCT cast(value as text) as value 
            FROM (SELECT (unnest(array_agg(row_to_json->>a.attname)))::text as value 
                  FROM (SELECT row_to_json(t) FROM ONLY pg_catalog.pg_class WHERE relname = p_table_name) x) y
        ) c1 ON true
        LEFT JOIN LATERAL (
            SELECT DISTINCT cast(value as text) as value 
            FROM (SELECT (unnest(array_agg(row_to_json->>a2.attname)))::text as value 
                  FROM (SELECT row_to_json(t2) FROM ONLY pg_catalog.pg_class WHERE relname = t2.relname) x) y
        ) c2 ON c1.value = c2.value
        WHERE t.relname = p_table_name 
        AND t2.relname != p_table_name
        AND a.attnum > 0 
        AND a2.attnum > 0
        AND NOT a.attisdropped
        AND NOT a2.attisdropped
        GROUP BY a.attname, t2.relname, a2.attname
        HAVING count(distinct c1.value) > 0
    )
    SELECT 
        column_name,
        ref_table,
        ref_column,
        (matching_values::numeric / distinct_values::numeric) * 100 as match_percentage
    FROM column_values
    WHERE matching_values::numeric / distinct_values::numeric > 0.8
    ORDER BY match_percentage DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to analyze and suggest default values
CREATE OR REPLACE FUNCTION analyze_default_values(p_table_name text)
RETURNS TABLE (
    column_name text,
    data_type text,
    current_default text,
    suggested_default text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.attname,
        pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
        COALESCE(pg_get_expr(d.adbin, d.adrelid), '') as current_default,
        CASE 
            WHEN pg_catalog.format_type(a.atttypid, a.atttypmod) LIKE '%timestamp%' 
                THEN 'CURRENT_TIMESTAMP'
            WHEN pg_catalog.format_type(a.atttypid, a.atttypmod) = 'boolean' 
                THEN 'false'
            WHEN pg_catalog.format_type(a.atttypid, a.atttypmod) = 'integer' 
                THEN '0'
            WHEN pg_catalog.format_type(a.atttypid, a.atttypmod) = 'text' 
                THEN ''''
            ELSE 'No suggestion'
        END as suggested_default
    FROM pg_attribute a
    LEFT JOIN pg_attrdef d ON a.attrelid = d.adrelid AND a.attnum = d.adnum
    JOIN pg_class t ON a.attrelid = t.oid
    WHERE t.relname = p_table_name 
    AND a.attnum > 0 
    AND NOT a.attisdropped;
END;
$$ LANGUAGE plpgsql;

-- Main function to analyze table and generate comprehensive report
CREATE OR REPLACE FUNCTION analyze_table_constraints(p_table_name text)
RETURNS text AS $$
DECLARE
    report text := '';
    unique_rec record;
    fk_rec record;
    default_rec record;
BEGIN
    report := report || 'Table Analysis Report for ' || p_table_name || E'\n\n';
    
    -- Unique constraints analysis
    report := report || 'Potential Unique Constraints:' || E'\n';
    FOR unique_rec IN SELECT * FROM analyze_unique_constraints(p_table_name) LOOP
        report := report || format('  Column: %s (Distinct ratio: %.2f%%) - %s', 
            unique_rec.column_name, 
            unique_rec.distinct_ratio * 100, 
            unique_rec.recommendation) || E'\n';
    END LOOP;
    
    -- Foreign key analysis
    report := report || E'\nPotential Foreign Key Relationships:' || E'\n';
    FOR fk_rec IN SELECT * FROM analyze_foreign_keys(p_table_name) LOOP
        report := report || format('  Column: %s might reference %s.%s (Match: %.2f%%)', 
            fk_rec.column_name, 
            fk_rec.potential_reference_table, 
            fk_rec.potential_reference_column,
            fk_rec.match_percentage) || E'\n';
    END LOOP;
    
    -- Default values analysis
    report := report || E'\nDefault Values Analysis:' || E'\n';
    FOR default_rec IN SELECT * FROM analyze_default_values(p_table_name) LOOP
        report := report || format('  Column: %s (%s)' || E'\n    Current default: %s' || E'\n    Suggested default: %s', 
            default_rec.column_name,
            default_rec.data_type,
            COALESCE(default_rec.current_default, 'none'),
            default_rec.suggested_default) || E'\n';
    END LOOP;
    
    RETURN report;
END;
$$ LANGUAGE plpgsql; 