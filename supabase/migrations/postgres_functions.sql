CREATE OR REPLACE FUNCTION check_user_id_foreign_keys()
RETURNS TABLE (
    table_name text,
    has_user_id boolean,
    has_proper_fk boolean,
    constraint_name text,
    deletion_rule text
) AS $$
BEGIN
    RETURN QUERY
    WITH tables_with_user_id AS (
        SELECT 
            t.table_schema || '.' || t.table_name as table_name,
            true as has_user_id
        FROM information_schema.columns c
        JOIN information_schema.tables t 
            ON c.table_name = t.table_name 
            AND c.table_schema = t.table_schema
        WHERE c.column_name = 'user_id'
        AND t.table_schema = 'public'
    ),
    foreign_keys AS (
        SELECT 
            tc.table_schema || '.' || tc.table_name as table_name,
            tc.constraint_name::text,
            rc.delete_rule::text
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.referential_constraints rc 
            ON tc.constraint_name = rc.constraint_name
        WHERE kcu.column_name = 'user_id'
        AND tc.constraint_type = 'FOREIGN KEY'
    )
    SELECT 
        t.table_name,
        true as has_user_id,
        COALESCE(fk.constraint_name IS NOT NULL, false) as has_proper_fk,
        COALESCE(fk.constraint_name, 'No Foreign Key')::text as constraint_name,
        COALESCE(fk.delete_rule, 'No Rule')::text as deletion_rule
    FROM tables_with_user_id t
    LEFT JOIN foreign_keys fk ON t.table_name = fk.table_name;
END;
$$ LANGUAGE plpgsql; 

-- Usage:
SELECT * FROM check_user_id_foreign_keys();

-- Step 1: Drop the existing foreign key constraint
-- ALTER TABLE public.experts 
-- DROP CONSTRAINT experts_user_id_fkey;

-- -- Step 2: Re-add the foreign key constraint with ON DELETE SET NULL
-- ALTER TABLE public.experts 
-- ADD CONSTRAINT experts_user_id_fkey 
-- FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL;


CREATE OR REPLACE FUNCTION find_orphaned_user_ids()
RETURNS TABLE (
    table_name text,
    column_name text,
    orphaned_user_id uuid,
    row_count bigint
) AS $$
BEGIN
    FOR table_name, column_name IN
        SELECT t.table_schema || '.' || t.table_name, c.column_name
        FROM information_schema.columns c
        JOIN information_schema.tables t 
            ON c.table_name = t.table_name 
            AND c.table_schema = t.table_schema
        WHERE c.column_name = 'user_id'
        AND t.table_schema = 'public'
    LOOP
        RETURN QUERY EXECUTE format(
            'SELECT %L::text, %L::text, user_id::uuid, COUNT(*)::bigint ' ||
            'FROM %s ' ||
            'WHERE user_id IS NOT NULL ' ||
            'AND NOT EXISTS (SELECT 1 FROM auth.users WHERE id = user_id) ' ||
            'GROUP BY user_id',
            table_name,
            column_name,
            table_name
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Usage:
SELECT * FROM find_orphaned_user_ids();-- 


add a foreign constraint one the domain_id on the sources table

add a foreign constraint one the expert_id on the sources table

add a foreign constraint one the parent_id on the sources table

add a foreign constraint one the created_by and updated_by field on the sources table

SELECT get_user_uuid_by_email('bunnage.ray@gmail.com');

SELECT get_domain_id_by_name('Dynamic Healing Group');

SELECT populate_sources_with_fixed_user_id(
    'bunnage.ray@gmail.com'
);
