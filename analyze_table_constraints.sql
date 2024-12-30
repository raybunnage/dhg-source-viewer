-- Function to analyze unique constraints
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
            (SELECT count(*) FROM pg_catalog.pg_class c WHERE c.relname = p_table_name) as total_rows
        FROM pg_attribute a
        JOIN pg_class t ON a.attrelid = t.oid
        LEFT JOIN pg_stats ON t.relname = pg_stats.tablename AND a.attname = pg_stats.attname
        WHERE t.relname = p_table_name AND a.attnum > 0 AND NOT a.attisdropped
    )
    SELECT 
        attname::text,
        COALESCE(
            CASE 
                WHEN n_distinct < 0 THEN abs(n_distinct)
                WHEN n_distinct > 0 THEN n_distinct / total_rows::numeric
                ELSE 0
            END,
            0
        )::numeric,
        (CASE 
            WHEN n_distinct < 0 AND abs(n_distinct) > 0.95 THEN 'Highly recommended for UNIQUE constraint'
            WHEN n_distinct > 0 AND (n_distinct / total_rows::numeric) > 0.95 THEN 'Consider UNIQUE constraint'
            ELSE 'Not recommended for UNIQUE constraint'
        END)::text
    FROM column_stats;
END;
$$ LANGUAGE plpgsql;

-- Main function to analyze table and generate comprehensive report
CREATE OR REPLACE FUNCTION analyze_table_constraints(p_table_name text)
RETURNS text AS $$
DECLARE
    report text := '';
    unique_rec record;
BEGIN
    -- Initialize report
    report := 'Table Analysis Report for ' || p_table_name || E'\n\n';
    
    -- Unique constraints analysis
    report := report || 'Potential Unique Constraints:' || E'\n';
    FOR unique_rec IN SELECT * FROM analyze_unique_constraints(p_table_name) LOOP
        report := report || format('  Column: %s (Distinct ratio: %s%%) - %s', 
            unique_rec.column_name, 
            round(unique_rec.distinct_ratio * 100, 2)::text, 
            unique_rec.recommendation) || E'\n';
    END LOOP;
    
    RETURN report;
END;
$$ LANGUAGE plpgsql;