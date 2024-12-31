import pytest
import pytest_asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from src.db.uni_document_types import DocumentTypes


@pytest_asyncio.fixture
async def supabase_client():
    """Fixture to create an authenticated Supabase client"""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    if not all([url, key, email, password]):
        raise ValueError("Missing required environment variables")

    client = SupabaseService(url, key)
    await client.login(email, password)
    return client


@pytest_asyncio.fixture
async def document_types(supabase_client):
    """Fixture to create a DocumentTypes instance"""
    return DocumentTypes(supabase_client)


@pytest.mark.asyncio
class TestDocumentTypes:
    async def test_add_and_delete_document(self, document_types):
        """Test adding and then deleting a document type"""
        # Add a test document
        doc = await document_types.add(
            document_type="Test Document",
            description="Test Description",
            mime_type="application/pdf",
            file_extension=".pdf",
            category="test",
            is_ai_generated=False,
        )

        assert doc is not None
        assert doc.get("document_type") == "Test Document"

        # Clean up
        assert await document_types.delete(doc["id"]) is True

    async def test_get_by_id(self, document_types):
        """Test getting a document by ID"""
        # First add a document
        doc = await document_types.add(
            document_type="Test Get By ID", description="Test Description"
        )

        # Get the document by ID
        retrieved_doc = await document_types.get_by_id(doc["id"])
        assert retrieved_doc["document_type"] == "Test Get By ID"

        # Clean up
        await document_types.delete(doc["id"])

    async def test_update_document(self, document_types):
        """Test updating a document"""
        # First add a document
        doc = await document_types.add(
            document_type="Test Update", description="Original Description"
        )

        # Update the document
        updated = await document_types.update(
            doc["id"], {"description": "Updated Description"}
        )

        assert updated["description"] == "Updated Description"

        # Clean up
        await document_types.delete(doc["id"])

    async def test_get_all(self, document_types):
        """Test getting all documents"""
        # Add a test document
        doc = await document_types.add(
            document_type="Test Get All", description="Test Description"
        )

        # Get all documents
        all_docs = await document_types.get_all()
        assert len(all_docs) > 0
        assert any(d["document_type"] == "Test Get All" for d in all_docs)

        # Clean up
        await document_types.delete(doc["id"])

    async def test_get_plus_by_name(self, document_types):
        """Test getting a document by name with optional fields"""
        # Add a test document
        doc = await document_types.add(
            document_type="Test Get By Name",
            description="Test Description",
            category="test_category",
        )

        # Get the document by name
        retrieved = await document_types.get_plus_by_name(
            "Test Get By Name", ["category"]
        )

        assert retrieved["document_type"] == "Test Get By Name"
        assert retrieved["category"] == "test_category"

        # Clean up
        await document_types.delete(doc["id"])

    async def test_invalid_document_type(self, document_types):
        """Test adding a document with invalid data"""
        with pytest.raises(ValueError):
            await document_types.add(document_type="")

    async def test_get_nonexistent_document(self, document_types):
        """Test getting a document that doesn't exist"""
        with pytest.raises(ValueError):
            await document_types.get_by_id("nonexistent-id")

    async def test_get_aliases(self, document_types):
        """Test getting aliases for a document type"""
        # Add a test document
        doc = await document_types.add(
            document_type="Test Aliases", description="Test Description"
        )

        # Get aliases (might be empty if no aliases exist)
        aliases = await document_types.get_aliases_by_document_type("Test Aliases")
        assert isinstance(aliases, list)

        # Clean up
        await document_types.delete(doc["id"])

    async def test_update_nonexistent_document(self, document_types):
        """Test updating a document that doesn't exist"""
        with pytest.raises(ValueError):
            await document_types.update(
                "nonexistent-id", {"description": "New Description"}
            )

    async def test_delete_nonexistent_document(self, document_types):
        """Test deleting a document that doesn't exist"""
        with pytest.raises(ValueError):
            await document_types.delete("nonexistent-id")

    async def test_duplicate_document_type(self, document_types):
        """Test adding a document with a duplicate name"""
        # Add first document
        doc = await document_types.add(
            document_type="Duplicate Test", description="First Document"
        )

        # Try to add duplicate
        with pytest.raises(ValueError):
            await document_types.add(
                document_type="Duplicate Test", description="Second Document"
            )

        # Clean up
        await document_types.delete(doc["id"])

    async def test_special_characters_in_document_type(self, document_types):
        """Test adding a document type with special characters"""
        special_name = "Test@#$%^&*()"
        doc = await document_types.add(
            document_type=special_name, description="Special Characters Test"
        )

        retrieved = await document_types.get_plus_by_name(special_name)
        assert retrieved["document_type"] == special_name

        # Clean up
        await document_types.delete(doc["id"])

    async def test_very_long_document_type(self, document_types):
        """Test adding a document type with a very long name"""
        long_name = "A" * 255  # Assuming 255 is the maximum length
        doc = await document_types.add(
            document_type=long_name, description="Long Name Test"
        )

        retrieved = await document_types.get_plus_by_name(long_name)
        assert retrieved["document_type"] == long_name

        # Clean up
        await document_types.delete(doc["id"])

    async def test_update_with_empty_values(self, document_types):
        """Test updating a document with empty values"""
        # First add a document
        doc = await document_types.add(
            document_type="Update Empty Test",
            description="Original Description",
            category="test_category",
        )

        # Try updating with empty values
        with pytest.raises(ValueError):
            await document_types.update(doc["id"], {"document_type": ""})

        # Clean up
        await document_types.delete(doc["id"])

    async def test_whitespace_only_document_type(self, document_types):
        """Test adding a document type with only whitespace"""
        with pytest.raises(ValueError):
            await document_types.add(document_type="   ", description="Whitespace Test")

    async def test_null_values_in_optional_fields(self, document_types):
        """Test adding a document with null values in optional fields"""
        doc = await document_types.add(
            document_type="Null Test",
            description="Test Description",
            mime_type=None,
            file_extension=None,
            category=None,
            is_ai_generated=None,
        )

        retrieved = await document_types.get_by_id(doc["id"])
        assert retrieved["document_type"] == "Null Test"
        assert retrieved["mime_type"] is None
        assert retrieved["file_extension"] is None

        # Clean up
        await document_types.delete(doc["id"])

    async def test_unicode_characters(self, document_types):
        """Test adding a document type with unicode characters"""
        unicode_name = "测试文档类型 🚀 Café"
        doc = await document_types.add(
            document_type=unicode_name, description="Unicode Test"
        )

        retrieved = await document_types.get_plus_by_name(unicode_name)
        assert retrieved["document_type"] == unicode_name

        # Clean up
        await document_types.delete(doc["id"])

    async def test_update_with_none_values(self, document_types):
        """Test updating optional fields to None"""
        doc = await document_types.add(
            document_type="Update None Test",
            description="Original Description",
            category="test_category",
            mime_type="application/pdf",
        )

        # Update with None values
        updated = await document_types.update(
            doc["id"], {"category": None, "mime_type": None}
        )

        assert updated["category"] is None
        assert updated["mime_type"] is None

        # Clean up
        await document_types.delete(doc["id"])

    async def test_leading_trailing_whitespace(self, document_types):
        """Test handling of leading/trailing whitespace in document type"""
        # Test that whitespace-containing document types are rejected
        with pytest.raises(ValueError):
            await document_types.add(
                document_type="  Whitespace Test  ", description="Whitespace Handling"
            )

        # Verify that properly formatted document type works
        doc = await document_types.add(
            document_type="Whitespace Test", description="Whitespace Handling"
        )

        # Clean up
        await document_types.delete(doc["id"])

    async def test_bulk_operations(self, document_types):
        """Test adding and retrieving multiple documents"""
        docs_to_add = [
            ("Bulk Test 1", "Description 1"),
            ("Bulk Test 2", "Description 2"),
            ("Bulk Test 3", "Description 3"),
        ]

        added_docs = []
        for doc_type, desc in docs_to_add:
            doc = await document_types.add(document_type=doc_type, description=desc)
            added_docs.append(doc)

        # Get all documents and verify
        all_docs = await document_types.get_all()
        for doc in added_docs:
            assert any(d["id"] == doc["id"] for d in all_docs)

        # Clean up
        for doc in added_docs:
            await document_types.delete(doc["id"])

    async def test_update_with_invalid_id_format(self, document_types):
        """Test updating with invalid ID format"""
        with pytest.raises(ValueError):
            await document_types.update("invalid-id-format", {"description": "Test"})


# pytest tests/test_uni_document_types.py -v
