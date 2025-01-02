import pytest
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import pytest_asyncio
import asyncio


project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService


@pytest_asyncio.fixture
async def supabase_service():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)
    await supabase.login(email, password)
    return supabase


async def insert_test_emails():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)
    await supabase.login(email, password)

    # Test single record insert
    single_email = {
        "email_id": "1",
        "subject": "Test Email 1",
        "content": "This is a test email body 1",
        "sender": "sender1@test.com",
        "to_recipients": "recipient1@test.com",
        "date": datetime.now(),
        "created_at": datetime.now(),
    }

    try:
        response = await supabase.insert_into_table("temp_emails", single_email)
        print("Single test email inserted successfully")
        print(f"Inserted email data: {response}")
    except Exception as e:
        print(f"Error inserting single test email: {e}")

    # Test multiple records insert
    test_emails = [
        {
            "email_id": str(i),
            "subject": f"Test Email {i}",
            "content": f"This is a test email body {i}",
            "sender": f"sender{i}@test.com",
            "to_recipients": f"recipient{i}@test.com",
            "date": datetime.now(),
            "created_at": datetime.now(),
        }
        for i in range(2, 4)
    ]

    try:
        response = await supabase.insert_into_table("temp_emails", test_emails)
        print("Multiple test emails inserted successfully")
        print(f"Inserted email data: {response}")
    except Exception as e:
        print(f"Error inserting multiple test emails: {e}")


async def test_login_and_get_user():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)

    # Attempt login
    login_response = await supabase.login(email, password)
    if not login_response:
        print("Login failed")
        return

    # Get user details
    user = await supabase.get_user()
    if user:
        print(f"Successfully retrieved user ID: {user.id}")
        print(f"User email: {user.email}")
    else:
        print("Failed to get user details")


async def test_domain_operations():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    supabase = SupabaseService(url, key)

    # Login first
    login_response = await supabase.login(email, password)
    if not login_response:
        print("Login failed")
        return

    # Get available domains
    try:
        domains = await supabase.select_from_table(
            "domains",
            ["id", "name"],
            where_filters=[("name", "eq", "Dynamic Healing Group")],
        )
        print("\nAvailable domains:")
        for domain in domains:
            print(f"- {domain['name']} (ID: {domain['id']})")

        # Find Dynamic Healing Group domain
        dhg_domain = next(
            (d for d in domains if d["name"] == "Dynamic Healing Group"), None
        )
        if dhg_domain:
            domain_id = dhg_domain["id"]
            print(f"\nFound Dynamic Healing Group domain ID: {domain_id}")

            # Set the domain
            await supabase.set_current_domain(domain_id)
            print("Successfully set domain to Dynamic Healing Group")

            # Get document types for the domain
            document_types = await supabase.select_from_table(
                "uni_document_types",
                ["id", "document_type", "description"],
            )
            print("\nDocument Types for this domain:")
            for doc_type in document_types:
                print(
                    f"- {doc_type['document_type']}: {doc_type.get('description', 'No description')}"
                )
        else:
            print("\nDynamic Healing Group domain not found")
            return
    except Exception as e:
        print(f"Error in domain operations: {e}")
        return

    # Rest of the existing test code...
    try:
        response = await supabase.select_from_table("some_domain_scoped_table", ["*"])
        print("Successfully queried domain-scoped table")
    except Exception as e:
        print(f"Error querying domain-scoped table: {e}")

    # Test clearing domain
    try:
        await supabase.set_current_domain(None)
        print("Successfully cleared domain")
    except Exception as e:
        print(f"Failed to clear domain: {e}")


if __name__ == "__main__":

    async def run_tests():
        # await test_login_and_get_user()
        await test_domain_operations()
        # await insert_test_emails()

    asyncio.run(run_tests())

# pytest tests/test_supabase_service.py
