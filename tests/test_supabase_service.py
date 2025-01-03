from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import pytest_asyncio
import asyncio
import pytest

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
from src.services.exceptions import (
    SupabaseConnectionError,
    SupabaseQueryError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    SupabaseError,
    SupabaseStorageError,
    map_storage_error,
)


project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService


# @pytest_asyncio.fixture
# async def supabase_service():
#     load_dotenv()
#     url = os.getenv("SUPABASE_URL")
#     key = os.getenv("SUPABASE_KEY")
#     email = os.getenv("TEST_EMAIL")
#     password = os.getenv("TEST_PASSWORD")

#     if not all([url, key, email, password]):
#         raise ValueError("Missing required environment variables")

#     supabase = SupabaseService(url, key)
#     await supabase.login(email, password)
#     return supabase


# async def insert_test_emails():
#     load_dotenv()
#     url = os.getenv("SUPABASE_URL")
#     key = os.getenv("SUPABASE_KEY")
#     email = os.getenv("TEST_EMAIL")
#     password = os.getenv("TEST_PASSWORD")

#     if not all([url, key, email, password]):
#         raise ValueError("Missing required environment variables")

#     supabase = SupabaseService(url, key)
#     await supabase.login(email, password)

#     # Test single record insert
#     single_email = {
#         "email_id": "1",
#         "subject": "Test Email 1",
#         "content": "This is a test email body 1",
#         "sender": "sender1@test.com",
#         "to_recipients": "recipient1@test.com",
#         "date": datetime.now(),
#         "created_at": datetime.now(),
#     }

#     try:
#         response = await supabase.insert_into_table("temp_emails", single_email)
#         print("Single test email inserted successfully")
#         print(f"Inserted email data: {response}")
#     except Exception as e:
#         print(f"Error inserting single test email: {e}")

#     # Test multiple records insert
#     test_emails = [
#         {
#             "email_id": str(i),
#             "subject": f"Test Email {i}",
#             "content": f"This is a test email body {i}",
#             "sender": f"sender{i}@test.com",
#             "to_recipients": f"recipient{i}@test.com",
#             "date": datetime.now(),
#             "created_at": datetime.now(),
#         }
#         for i in range(2, 4)
#     ]

#     try:
#         response = await supabase.insert_into_table("temp_emails", test_emails)
#         print("Multiple test emails inserted successfully")
#         print(f"Inserted email data: {response}")
#     except Exception as e:
#         print(f"Error inserting multiple test emails: {e}")


# async def test_login_and_get_user():
#     load_dotenv()
#     url = os.getenv("SUPABASE_URL")
#     key = os.getenv("SUPABASE_KEY")
#     email = os.getenv("TEST_EMAIL")
#     password = os.getenv("TEST_PASSWORD")

#     if not all([url, key, email, password]):
#         raise ValueError("Missing required environment variables")

#     supabase = SupabaseService(url, key)

#     # Attempt login
#     login_response = await supabase.login(email, password)
#     if not login_response:
#         print("Login failed")
#         return

#     # Get user details
#     user = await supabase.get_user()
#     if user:
#         print(f"Successfully retrieved user ID: {user.id}")
#         print(f"User email: {user.email}")
#     else:
#         print("Failed to get user details")


# async def test_domain_operations():
#     load_dotenv()
#     url = os.getenv("SUPABASE_URL")
#     key = os.getenv("SUPABASE_KEY")
#     email = os.getenv("TEST_EMAIL")
#     password = os.getenv("TEST_PASSWORD")

#     if not all([url, key, email, password]):
#         raise ValueError("Missing required environment variables")

#     supabase = SupabaseService(url, key)

#     # Login first
#     login_response = await supabase.login(email, password)
#     if not login_response:
#         print("Login failed")
#         return

#     # Get available domains
#     try:
#         domains = await supabase.select_from_table(
#             "domains",
#             ["id", "name"],
#             where_filters=[("name", "eq", "Dynamic Healing Group")],
#         )
#         print("\nAvailable domains:")
#         for domain in domains:
#             print(f"- {domain['name']} (ID: {domain['id']})")

#         # Find Dynamic Healing Group domain
#         dhg_domain = next(
#             (d for d in domains if d["name"] == "Dynamic Healing Group"), None
#         )
#         if dhg_domain:
#             domain_id = dhg_domain["id"]
#             print(f"\nFound Dynamic Healing Group domain ID: {domain_id}")

#             # Set the domain
#             await supabase.set_current_domain(domain_id)
#             print("Successfully set domain to Dynamic Healing Group")

#             # Get document types for the domain
#             document_types = await supabase.select_from_table(
#                 "uni_document_types",
#                 ["id", "document_type", "description"],
#             )
#             print("\nDocument Types for this domain:")
#             for doc_type in document_types:
#                 print(
#                     f"- {doc_type['document_type']}: {doc_type.get('description', 'No description')}"
#                 )
#         else:
#             print("\nDynamic Healing Group domain not found")
#             return
#     except Exception as e:
#         print(f"Error in domain operations: {e}")
#         return

#     # Rest of the existing test code...
#     try:
#         response = await supabase.select_from_table("some_domain_scoped_table", ["*"])
#         print("Successfully queried domain-scoped table")
#     except Exception as e:
#         print(f"Error querying domain-scoped table: {e}")

#     # Test clearing domain
#     try:
#         await supabase.set_current_domain(None)
#         print("Successfully cleared domain")
#     except Exception as e:
#         print(f"Failed to clear domain: {e}")


async def test_connection():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    # Test successful connection
    try:
        supabase = SupabaseService(url, key)
        print("✓ Connection successful")
    except SupabaseConnectionError as e:
        print(f"✗ Connection failed: {e}")

    # Test connection failure
    try:
        supabase_invalid = SupabaseService("invalid_url", "invalid_key")
        print("✗ Expected connection failure, but got success")
    except SupabaseConnectionError as e:
        print("✓ Successfully caught connection error with invalid credentials")


async def test_query_operations():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    supabase = SupabaseService(url, key)
    await supabase.login(email, password)

    # Test successful query
    try:
        result = await supabase.select_from_table("domains", {"id": True, "name": True})
        print("✓ Query executed successfully")
        print(f"  Retrieved {len(result)} records")
    except SupabaseQueryError as e:
        print(f"✗ Query failed: {e}")

    # Test invalid table query
    try:
        result = await supabase.select_from_table("nonexistent_table", "id")
        print("✗ Expected query failure, but got success")
    except SupabaseQueryError as e:
        print("✓ Successfully caught query error for invalid table")

    # Test invalid column query
    try:
        result = await supabase.select_from_table("domains", "nonexistent_column")
        print("✗ Expected query failure, but got success")
    except SupabaseQueryError as e:
        print("✓ Successfully caught query error for invalid column")


async def test_authentication():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    print(f"\nDebug Info:")
    print(f"URL exists: {bool(url)}")
    print(f"Key exists: {bool(key)}")
    print(f"Email exists: {bool(email)}")
    print(f"Password exists: {bool(password)}")

    try:
        supabase = SupabaseService(url, key)
        print("✓ Supabase service initialized")

        if not supabase.supabase:
            print("✗ Supabase client is None after initialization")
            return

        print("Attempting login...")
        try:
            await supabase.login(email, password)
            user = await supabase.get_user()
            print("✓ Login successful")
            print(f"  User ID: {user.id}")
        except SupabaseAuthenticationError as e:
            print(f"✗ Login failed with SupabaseAuthenticationError: {str(e)}")
            if hasattr(e, "original_error"):
                print(f"Original error: {str(e.original_error)}")
        except Exception as e:
            print(f"✗ Login failed with unexpected error: {str(e)}")
            print(f"Error type: {type(e)}")
    except Exception as e:
        print(f"✗ Service initialization failed: {str(e)}")
        print(f"Error type: {type(e)}")

    # Test invalid credentials
    try:
        await supabase.login("invalid@email.com", "wrongpassword")
        print("✗ Expected login failure, but got success")
    except SupabaseAuthenticationError as e:
        print("✓ Successfully caught invalid login attempt")


async def test_domain_management():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    supabase = SupabaseService(url, key)
    await supabase.login(email, password)

    # Test setting valid domain
    try:
        domains = await supabase.select_from_table(
            "domains",
             {"id": True, "name": True},
            where_filters=[("name", "eq", "Dynamic Healing Group")],
        )
        if domains:
            await supabase.set_current_domain(domains[0]["id"])
            print("✓ Domain set successfully")
        else:
            print("✗ Test domain not found")
    except SupabaseQueryError as e:
        print(f"✗ Failed to set domain: {e}")

    # Test setting invalid domain
    try:
        await supabase.set_current_domain("invalid_domain_id")
        print("✗ Expected domain setting failure, but got success")
    except SupabaseAuthorizationError as e:
        print("✓ Successfully caught invalid domain setting")

    # Test clearing domain
    try:
        await supabase.set_current_domain(None)
        print("✓ Domain cleared successfully")
    except SupabaseError as e:
        print(f"✗ Failed to clear domain: {e}")


# @pytest.mark.asyncio
# async def test_storage_operations(supabase_service):
#     """Test storage operations and their exceptions"""

#     # Test invalid bucket name
#     with pytest.raises(ValueError):
#         await supabase_service.upload_file("", "test.txt", b"test data")

#     # Test non-existent bucket
#     with pytest.raises(SupabaseStorageNotFoundError):
#         await supabase_service.upload_file(
#             "nonexistent_bucket", "test.txt", b"test data"
#         )

#     # Test unauthorized access
#     invalid_service = SupabaseService(os.getenv("SUPABASE_URL"), "invalid_key")
#     with pytest.raises(SupabaseStorageAuthError):
#         await invalid_service.upload_file("test_bucket", "test.txt", b"test data")


# @pytest.mark.asyncio
# async def test_query_operations(supabase_service):
#     """Test query operations and their exceptions"""

#     # Test invalid table name
#     with pytest.raises(ValueError):
#         await supabase_service.select_from_table("", ["*"])

#     # Test non-existent table
#     with pytest.raises(SupabaseQueryError):
#         await supabase_service.select_from_table("nonexistent_table", ["*"])

#     # Test invalid column
#     with pytest.raises(SupabaseQueryError):
#         await supabase_service.select_from_table("domains", ["nonexistent_column"])

#     # Test successful query
#     try:
#         result = await supabase_service.select_from_table("domains", ["id", "name"])
#         assert result is not None, "Query should return data"
#     except SupabaseError as e:
#         pytest.fail(f"Query should not raise exception: {e}")


# @pytest.mark.asyncio
# async def test_authentication_errors(supabase_service):
#     """Test authentication error handling"""

#     # Test invalid credentials
#     with pytest.raises(SupabaseAuthenticationError):
#         await supabase_service.login("invalid@email.com", "wrongpassword")

#     # Test missing credentials
#     with pytest.raises(SupabaseError):
#         await supabase_service.login("", "")


if __name__ == "__main__":

    async def run_all_tests():
        print("\n=== Testing Connection ===")
        await test_connection()

        print("\n=== Testing Query Operations ===")
        await test_query_operations()

        print("\n=== Testing Authentication ===")
        await test_authentication()

        print("\n=== Testing Domain Management ===")
        await test_domain_management()

    asyncio.run(run_all_tests())

# pytest tests/test_supabase_service.py
