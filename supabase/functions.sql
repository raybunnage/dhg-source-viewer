-- First, drop the existing function
DROP FUNCTION IF EXISTS public.get_table_columns_plus(text);

-- Then create the new function
CREATE OR REPLACE FUNCTION public.get_table_columns_plus(p_table_name text)
RETURNS TABLE(
    ordinal_position integer, 
    column_name text, 
    data_type text, 
    is_nullable text, 
    column_default text, 
    is_unique text,
    unique_constraint_name text,
    foreign_key text, 
    trigger_name text
) 
LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    WITH base_columns AS (
        SELECT DISTINCT
            c.ordinal_position::integer,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default
        FROM 
            information_schema.columns c
        WHERE 
            c.table_schema = 'public' 
            AND c.table_name = p_table_name
    ),
    unique_constraints AS (
        SELECT DISTINCT
            kcu.column_name,
            'YES' as is_unique,
            tc.constraint_name as unique_constraint_name
        FROM 
            information_schema.key_column_usage kcu 
        JOIN 
            information_schema.table_constraints tc 
            ON kcu.constraint_name = tc.constraint_name 
            AND kcu.table_schema = tc.table_schema
        WHERE 
            kcu.table_schema = 'public' 
            AND kcu.table_name = p_table_name
            AND tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
    ),
    foreign_keys AS (
        SELECT DISTINCT
            kcu.column_name,
            fk.constraint_name as foreign_key
        FROM 
            information_schema.key_column_usage kcu 
        JOIN 
            information_schema.table_constraints tc 
            ON kcu.constraint_name = tc.constraint_name 
        JOIN 
            information_schema.referential_constraints rc 
            ON tc.constraint_name = rc.constraint_name 
        JOIN 
            information_schema.table_constraints fk 
            ON rc.unique_constraint_name = fk.constraint_name 
        WHERE 
            kcu.table_schema = 'public' 
            AND kcu.table_name = p_table_name
    ),
    triggers AS (
        SELECT DISTINCT
            t.tgname as table_trigger_name
        FROM 
            pg_trigger t 
        WHERE 
            t.tgrelid = (SELECT oid FROM pg_class WHERE relname = p_table_name AND relnamespace = 'public'::regnamespace)
    )
    SELECT 
        bc.ordinal_position,
        bc.column_name::text,
        bc.data_type::text,
        bc.is_nullable::text,
        bc.column_default::text,
        COALESCE(uc.is_unique, 'NO')::text as is_unique,
        uc.unique_constraint_name::text,
        fk.foreign_key::text,
        (SELECT table_trigger_name::text FROM triggers LIMIT 1) as trigger_name
    FROM 
        base_columns bc
        LEFT JOIN unique_constraints uc ON bc.column_name = uc.column_name
        LEFT JOIN foreign_keys fk ON bc.column_name = fk.column_name
    ORDER BY 
        bc.ordinal_position;
END;
$function$;

-- Function to handle updating the updated_at timestamp
CREATE OR REPLACE FUNCTION handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for multiple tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT DISTINCT c.table_name 
        FROM information_schema.columns c
        LEFT JOIN pg_trigger tg ON tg.tgrelid = (c.table_name::regclass)
        WHERE c.column_name = 'updated_at' 
        AND c.table_schema = 'public'
        AND tg.tgname IS NULL
    LOOP
        EXECUTE format('
            CREATE TRIGGER set_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION handle_updated_at();
        ', t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'set_updated_at' 
        AND tgrelid = 'experts'::regclass
    ) THEN
        CREATE TRIGGER set_updated_at
            BEFORE UPDATE ON experts
            FOR EACH ROW
            EXECUTE FUNCTION handle_updated_at();
    END IF;
END;
$$ LANGUAGE plpgsql;