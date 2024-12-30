import psycopg2
import os

db_params = {
    "host": "db.jdksnfkupzywjdfefkyj.supabase.co",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": os.getenv("SUPABASE_DB_PASSWORD"),
    "sslmode": "require",
}

try:
    connection = psycopg2.connect(**db_params)
    print("Connection successful!")
except Exception as e:
    print(f"Error connecting to the database: {e}")