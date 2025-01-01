CREATE OR REPLACE FUNCTION get_table_columns_with_unique(p_table_name text)
RETURNS TABLE(column_name text, data_type text, is_nullable text, column_default text, is_unique text) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.column_name, 
        c.data_type, 
        c.is_nullable, 
        c.column_default,
        CASE 
            WHEN kcu.column_name IS NOT NULL THEN 'YES' 
            ELSE 'NO' 
        END AS is_unique
    FROM 
        information_schema.columns c
    LEFT JOIN 
        information_schema.key_column_usage kcu 
        ON c.table_name = kcu.table_name 
        AND c.column_name = kcu.column_name 
        AND c.table_schema = kcu.table_schema
    LEFT JOIN 
        information_schema.table_constraints tc 
        ON kcu.constraint_name = tc.constraint_name 
        AND kcu.table_schema = tc.table_schema
    WHERE 
        c.table_schema = 'public' 
        AND c.table_name = p_table_name;
        -- AND tc.constraint_type = 'UNIQUE';
END;
$$ LANGUAGE plpgsql;