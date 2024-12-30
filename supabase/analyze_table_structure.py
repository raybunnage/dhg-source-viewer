import psycopg2
from typing import Dict, List, Set
from collections import defaultdict
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import socket

load_dotenv()


def analyze_table_structure(
    supabase_url: str, supabase_key: str, schema: str, table_name: str
) -> Dict:
    """
    Performs comprehensive analysis of a PostgreSQL table in Supabase.

    Args:
        supabase_url (str): Supabase project URL
        supabase_key (str): Supabase service_role key (needs postgres access)
        schema (str): Schema name (usually 'public')
        table_name (str): Table to analyze

    Returns:
        Dict containing analysis results and recommendations
    """

    try:
        # Parse Supabase URL to get connection details
        url = urlparse(supabase_url)
        host = url.hostname
        project_ref = host.split(".")[0]  # Extract project reference

        # Force IPv4
        try:
            host = "db.jdksnfkupzywjdfefkyj.supabase.co"
            print(f"Attempting to connect to {host}")

            # Try multiple known Supabase IPs
            possible_ips = [
                "104.198.35.144",  # Common Supabase IP
                "159.89.214.31",  # Alternative IP
                "24.199.96.251",  # Another alternative
            ]

            # Try each IP until one works
            for ip_address in possible_ips:
                try:
                    print(f"Attempting connection with IP: {ip_address}")
                    db_params = {
                        "hostaddr": ip_address,  # Use IP directly
                        "host": host,  # Keep original hostname for SSL verification
                        "port": 5432,
                        "dbname": "postgres",
                        "user": "postgres",
                        "password": os.getenv("SUPABASE_DB_PASSWORD"),
                        "sslmode": "require",
                        "connect_timeout": 10,
                        "server_hostname": host,  # Add server hostname for SSL verification
                    }

                    conn = psycopg2.connect(**db_params)
                    print(f"Successfully connected using IP: {ip_address}")
                    break
                except Exception as e:
                    print(f"Failed to connect with IP {ip_address}: {str(e)}")
                    continue
            else:
                raise Exception("Failed to connect using any known IP addresses")

        except Exception as e:
            print(f"Connection error: {str(e)}")
            raise

        cur = conn.cursor()

        analysis = {
            "missing_foreign_keys": [],
            "missing_constraints": [],
            "missing_indices": [],
            "recommended_unique_constraints": [],
            "general_recommendations": [],
        }

        # Get column information
        cur.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s;
        """,
            (schema, table_name),
        )
        columns = cur.fetchall()

        # Get existing constraints
        cur.execute(
            """
            SELECT c.conname, c.contype, 
                   array_agg(a.attname) as columns,
                   confrelid::regclass as referenced_table
            FROM pg_constraint c
            JOIN pg_attribute a ON a.attnum = ANY(c.conkey)
            WHERE c.conrelid = %s::regclass
            GROUP BY c.conname, c.contype, c.confrelid;
        """,
            (f"{schema}.{table_name}",),
        )
        existing_constraints = cur.fetchall()

        # Analyze potential foreign keys
        for column in columns:
            col_name = column[0]
            data_type = column[1]

            # Check for potential foreign key columns (names ending with _id)
            if col_name.lower().endswith("_id"):
                referenced_table = col_name[:-3]
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name = %s
                    );
                """,
                    (schema, referenced_table),
                )

                if cur.fetchone()[0]:
                    # Check if foreign key already exists
                    if not any(
                        c[1] == "f" and col_name in c[2] for c in existing_constraints
                    ):
                        analysis["missing_foreign_keys"].append(
                            {
                                "column": col_name,
                                "referenced_table": referenced_table,
                                "sql": f"""
                                ALTER TABLE {schema}.{table_name}
                                ADD CONSTRAINT fk_{table_name}_{col_name}
                                FOREIGN KEY ({col_name})
                                REFERENCES {schema}.{referenced_table} (id);
                            """,
                            }
                        )

        # Analyze for missing constraints
        for column in columns:
            col_name = column[0]
            data_type = column[1]
            is_nullable = column[2]

            # Check for email columns
            if "email" in col_name.lower():
                analysis["missing_constraints"].append(
                    {
                        "column": col_name,
                        "type": "CHECK",
                        "sql": f"""
                        ALTER TABLE {schema}.{table_name}
                        ADD CONSTRAINT check_{col_name}_email_format
                        CHECK (email ~* {repr(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')});
                    """,
                    }
                )

            # Check for date columns
            if data_type in ("date", "timestamp"):
                analysis["missing_constraints"].append(
                    {
                        "column": col_name,
                        "type": "CHECK",
                        "sql": f"""
                        ALTER TABLE {schema}.{table_name}
                        ADD CONSTRAINT check_{col_name}_reasonable_date
                        CHECK ({col_name} >= '1900-01-01'::date);
                    """,
                    }
                )

            # Suggest NOT NULL for important-looking columns
            if is_nullable == "YES" and any(
                keyword in col_name.lower()
                for keyword in ["name", "email", "phone", "address", "status"]
            ):
                analysis["missing_constraints"].append(
                    {
                        "column": col_name,
                        "type": "NOT NULL",
                        "sql": f"""
                        ALTER TABLE {schema}.{table_name}
                        ALTER COLUMN {col_name} SET NOT NULL;
                    """,
                    }
                )

        # Analyze for missing indices
        cur.execute(
            """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s;
        """,
            (schema, table_name),
        )
        existing_indices = cur.fetchall()

        # Suggest indices for foreign keys and frequently queried columns
        for constraint in existing_constraints:
            if constraint[1] == "f":  # Foreign key
                col_name = constraint[2][0]
                if not any(col_name in idx[1] for idx in existing_indices):
                    analysis["missing_indices"].append(
                        {
                            "column": col_name,
                            "sql": f"""
                            CREATE INDEX idx_{table_name}_{col_name}
                            ON {schema}.{table_name} ({col_name});
                        """,
                        }
                    )

        # Analyze for unique constraints
        for column in columns:
            col_name = column[0]
            if any(
                keyword in col_name.lower()
                for keyword in ["email", "username", "code", "number"]
            ):
                if not any(
                    c[1] == "u" and col_name in c[2] for c in existing_constraints
                ):
                    analysis["recommended_unique_constraints"].append(
                        {
                            "column": col_name,
                            "sql": f"""
                            ALTER TABLE {schema}.{table_name}
                            ADD CONSTRAINT unq_{table_name}_{col_name}
                            UNIQUE ({col_name});
                        """,
                        }
                    )

        # General recommendations
        analysis["general_recommendations"].extend(
            [
                "Consider adding a created_at TIMESTAMP column with default CURRENT_TIMESTAMP",
                "Consider adding an updated_at TIMESTAMP column with trigger for updates",
                "Consider adding a soft delete column (deleted_at TIMESTAMP) instead of hard deletes",
            ]
        )

        cur.close()
        conn.close()
        return analysis

    except Exception as e:
        print(f"Error analyzing table: {str(e)}")
        return None


# Example usage:
if __name__ == "__main__":
    print(f"URL: {os.getenv('SUPABASE_URL')}")
    print(
        f"Key: {os.getenv('SUPABASE_DB_PASSWORD')[:5]}..."
    )  # Print first 5 chars only for security
    results = analyze_table_structure(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_DB_PASSWORD"),
        schema="public",
        table_name="emails",
    )

    if results is None:
        print(
            "Error: Could not analyze table structure. Please check your connection settings."
        )
    else:
        # Print results in a formatted way
        for category, items in results.items():
            print(f"\n=== {category.replace('_', ' ').title()} ===")
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        print(f"\nColumn: {item.get('column', 'N/A')}")
                        if "sql" in item:
                            print("SQL to implement:")
                            print(item["sql"].strip())
                    else:
                        print(f"- {item}")


# def get_test_users(self):
#         # The client automatically handles authentication after login
#         return self.supabase.table("test").select("*").execute()

#     def get_todos(self):
#         data = self.supabase.table("todos").select("*").execute()
#         return data