# SELECT 
#     'CREATE TABLE ' || tablename || ' (' || string_agg(column_definition, ', ' ORDER BY ordinal_position) || ');'
# FROM (
#     SELECT 
#         t.tablename,
#         c.ordinal_position,
#         c.column_name || ' ' || c.data_type || 
#         CASE WHEN c.character_maximum_length IS NOT NULL 
#              THEN '(' || c.character_maximum_length || ')'
#              ELSE '' 
#         END ||
#         CASE WHEN c.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
#         CASE WHEN c.column_default IS NOT NULL 
#              THEN ' DEFAULT ' || c.column_default 
#              ELSE '' 
#         END as column_definition
#     FROM pg_catalog.pg_tables t
#     JOIN information_schema.columns c 
#          ON t.tablename = c.table_name
#     WHERE t.schemaname = 'public'
# ) subquery
# GROUP BY tablename;


# SELECT 
#     'CREATE TABLE ' || tablename || ' (' || 
#     string_agg(column_definition, ', ' ORDER BY ordinal_position) || 
#     ');'
# FROM (
#     SELECT 
#         t.tablename,
#         c.ordinal_position,
#         c.column_name || ' ' || c.data_type || 
#         CASE WHEN c.character_maximum_length IS NOT NULL 
#              THEN '(' || c.character_maximum_length || ')'
#              ELSE '' 
#         END ||
#         CASE WHEN c.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
#         CASE WHEN c.column_default IS NOT NULL 
#              THEN ' DEFAULT ' || c.column_default 
#              ELSE '' 
#         END as column_definition
#     FROM pg_catalog.pg_tables t
#     JOIN information_schema.columns c 
#          ON t.tablename = c.table_name
#     WHERE t.schemaname = 'public' 
#     AND t.tablename = 'your_table_name'  -- Replace with your table name
# ) subquery
# GROUP BY tablename;


# SELECT column_name, data_type, is_nullable, column_default
# FROM information_schema.columns
# WHERE table_schema = 'public' 
# AND table_name = 'experts';