from pathlib import Path
import sys
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService




def migrate_emails_to_supabase():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect("/Users/raybunnage/Documents/github/dhg-knowledge-tool-2/DynamicHealing.db")
    sqlite_cursor = sqlite_conn.cursor()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    # Get Supabase client

    # Fetch all emails from SQLite
    sqlite_cursor.execute("""
        SELECT email_id, date, sender, subject, to_recipients, content, 
               attachment_cnt, url_cnt, is_ai_process_for_concepts, contents_length, is_in_contents, is_in_concepts, created_at, is_valid 
        FROM emails
    """)

# CREATE TABLE emails (
#         email_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         date DATETIME,
#         sender TEXT,
#         subject TEXT,
#         to_recipients TEXT,
#         content TEXT,
#         attachment_cnt INTEGER,
#         url_cnt INTEGER
    # , is_ai_process_for_concepts INTEGER, contents_length INTEGER, is_in_contents INTEGER, is_in_concepts INTEGER, created_at TIMESTAMP, is_valid INTEGER)


    # Convert to list of dictionaries
    emails = []
    for row in sqlite_cursor.fetchall():
        email = {
            "email_id": row[0],
            "date": row[1],
            "sender": row[2],
            "subject": row[3],
            "to_recipients": row[4],
            "content": row[5],
            "attachment_cnt": row[6],
            "url_cnt": row[7],
            "is_ai_process_for_concepts": row[8],
            "contents_length": row[9],
            "is_in_contents": row[10],
            "is_in_concepts": row[11],
            "created_at": row[12],
            "is_valid": row[13],
        }
        emails.append(email)

    # Insert in batches to avoid memory issues
    BATCH_SIZE = 100
    for i in range(0, len(emails), BATCH_SIZE):
        batch = emails[i : i + BATCH_SIZE]
        result = supabase.insert_into_table("temp_emails", batch)
        if result:
            print(len(result))
        print(f"Inserted batch {i//BATCH_SIZE + 1} of {len(emails)//BATCH_SIZE + 1}")

    # Close SQLite connection
    sqlite_conn.close()


def migrate_attachments_to_supabase():
    sqlite_conn = sqlite3.connect("path/to/your/sqlite.db")
    sqlite_cursor = sqlite_conn.cursor()

    supabase = get_supabase_client()

    sqlite_cursor.execute("""
        SELECT email_id, filename, size, created_at 
        FROM attachments
    """)

    attachments = []
    for row in sqlite_cursor.fetchall():
        attachment = {
            "email_id": row[0],
            "filename": row[1],
            "size": row[2],
            "created_at": row[3] or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        attachments.append(attachment)

    BATCH_SIZE = 100
    for i in range(0, len(attachments), BATCH_SIZE):
        batch = attachments[i : i + BATCH_SIZE]
        result = supabase.table("attachments").insert(batch).execute()
        print(
            f"Inserted batch {i//BATCH_SIZE + 1} of {len(attachments)//BATCH_SIZE + 1}"
        )

    sqlite_conn.close()


def migrate_urls_to_supabase():
    sqlite_conn = sqlite3.connect("path/to/your/sqlite.db")
    sqlite_cursor = sqlite_conn.cursor()

    supabase = get_supabase_client()

    sqlite_cursor.execute("""
        SELECT email_id, url, created_at 
        FROM all_email_urls
    """)

    urls = []
    for row in sqlite_cursor.fetchall():
        url = {
            "email_id": row[0],
            "url": row[1],
            "created_at": row[2] or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        urls.append(url)

    BATCH_SIZE = 100
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        result = supabase.table("all_email_urls").insert(batch).execute()
        print(f"Inserted batch {i//BATCH_SIZE + 1} of {len(urls)//BATCH_SIZE + 1}")

    sqlite_conn.close()


if __name__ == "__main__":
    print("Starting migration...")
    print("Migrating emails...")
    migrate_emails_to_supabase()
    # print("Migrating attachments...")
    # migrate_attachments_to_supabase()
    # print("Migrating URLs...")
    # migrate_urls_to_supabase()
    # print("Migration complete!")
