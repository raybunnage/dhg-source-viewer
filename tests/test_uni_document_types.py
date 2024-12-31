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


# pytest tests/test_uni_document_types.py -v
