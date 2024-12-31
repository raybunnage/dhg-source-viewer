import pytest
import pytest_asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import asyncio

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService
from src.db.experts import Experts


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
async def experts(supabase_client):
    """Fixture to create an Experts instance"""
    return Experts(supabase_client)


@pytest.mark.asyncio
class TestExperts:
    async def test_add_and_delete_expert(self, experts):
        """Test adding and then deleting an expert"""
        expert = await experts.add(
            expert_name="Test Expert",
            full_name="Test Expert Full Name",
            email_address="test@example.com",
        )

        assert expert is not None
        assert expert.get("expert_name") == "Test Expert"
        assert expert.get("full_name") == "Test Expert Full Name"

        # Clean up
        assert await experts.delete(expert["id"]) is True

    async def test_get_by_id(self, experts):
        """Test getting an expert by ID"""
        expert = await experts.add(
            expert_name="Test Get By ID", full_name="Get By ID Full Name"
        )

        retrieved = await experts.get_by_id(expert["id"])
        assert retrieved["expert_name"] == "Test Get By ID"
        assert retrieved["full_name"] == "Get By ID Full Name"

        await experts.delete(expert["id"])

    async def test_update_expert(self, experts):
        """Test updating an expert"""
        expert = await experts.add(
            expert_name="Test Update", full_name="Original Full Name"
        )

        updated = await experts.update(
            expert["id"],
            {"full_name": "Updated Full Name", "expertise_area": "Machine Learning"},
        )

        assert updated["full_name"] == "Updated Full Name"
        assert updated["expertise_area"] == "Machine Learning"

        await experts.delete(expert["id"])

    async def test_get_all(self, experts):
        """Test getting all experts"""
        expert = await experts.add(
            expert_name="Test Get All", full_name="Get All Full Name"
        )

        all_experts = await experts.get_all()
        assert len(all_experts) > 0
        assert any(e["expert_name"] == "Test Get All" for e in all_experts)

        await experts.delete(expert["id"])

    async def test_get_plus_by_name(self, experts):
        """Test getting an expert by name with optional fields"""
        expert = await experts.add(
            expert_name="Test Get By Name",
            full_name="Get By Name Full",
            additional_fields={"expertise_area": "AI Research", "experience_years": 10},
        )

        retrieved = await experts.get_plus_by_name(
            "Test Get By Name", ["expertise_area", "experience_years"]
        )

        assert retrieved["expert_name"] == "Test Get By Name"
        assert retrieved["expertise_area"] == "AI Research"
        assert retrieved["experience_years"] == 10

        await experts.delete(expert["id"])

    async def test_add_with_all_fields(self, experts):
        """Test adding an expert with all available fields"""
        expert = await experts.add(
            expert_name="Complete Expert",
            full_name="Complete Expert Full Name",
            email_address="complete@example.com",
            additional_fields={
                "expertise_area": "Data Science",
                "experience_years": 15,
                "bio": "Expert in data science",
                "is_in_core_group": True,
            },
        )

        assert expert["expert_name"] == "Complete Expert"
        assert expert["expertise_area"] == "Data Science"
        assert expert["experience_years"] == 15

        await experts.delete(expert["id"])

    async def test_add_alias_and_get_aliases(self, experts):
        """Test adding and retrieving aliases for an expert"""
        # Create the expert
        expert = await experts.add(
            expert_name="Original Name", full_name="Original Full Name"
        )
        assert expert is not None, "Failed to create expert"

        # Add the alias
        alias = await experts.add_alias("Original Name", "Alias Name")
        assert alias is not None, "Failed to create alias"
        print(f"Created alias: {alias}")

        # Get aliases
        aliases = await experts.get_aliases_by_expert_name("Original Name")
        print(f"Retrieved aliases: {aliases}")

        # More specific assertions
        assert aliases is not None, "Aliases should not be None"
        assert len(aliases) > 0, f"Expected at least one alias, got {aliases}"
        assert any(
            a["alias_name"] == "Alias Name" for a in aliases
        ), "Expected alias not found"

        # Clean up
        if alias:
            await experts.delete_alias(alias["id"])
        await experts.delete(expert["id"])

    async def test_invalid_expert_name(self, experts):
        """Test adding an expert with invalid data"""
        with pytest.raises(ValueError):
            await experts.add(expert_name="", full_name="Invalid Expert")

    async def test_get_nonexistent_expert(self, experts):
        """Test getting an expert that doesn't exist"""
        with pytest.raises(ValueError):
            await experts.get_by_id("nonexistent-id")

    async def test_unicode_characters(self, experts):
        """Test adding an expert with unicode characters"""
        unicode_name = "专家测试 🤖 Señor"
        expert = await experts.add(
            expert_name=unicode_name, full_name="Unicode Test Expert"
        )

        retrieved = await experts.get_plus_by_name(unicode_name)
        assert retrieved["expert_name"] == unicode_name

        await experts.delete(expert["id"])

    async def test_update_with_none_values(self, experts):
        """Test updating optional fields to None"""
        expert = await experts.add(
            expert_name="Update None Test",
            full_name="Update None Full Name",
            email_address="test@example.com",
        )

        updated = await experts.update(expert["id"], {"email_address": None})

        assert updated["email_address"] is None

        await experts.delete(expert["id"])

    async def test_bulk_operations(self, experts):
        """Test adding and retrieving multiple experts"""
        experts_to_add = [
            ("Bulk Test 1", "Full Name 1"),
            ("Bulk Test 2", "Full Name 2"),
            ("Bulk Test 3", "Full Name 3"),
        ]

        added_experts = []
        for expert_name, full_name in experts_to_add:
            expert = await experts.add(expert_name=expert_name, full_name=full_name)
            added_experts.append(expert)

        all_experts = await experts.get_all()
        for expert in added_experts:
            assert any(e["id"] == expert["id"] for e in all_experts)

        for expert in added_experts:
            await experts.delete(expert["id"])

    async def test_concurrent_updates(self, experts):
        """Test concurrent updates to the same expert"""
        expert = await experts.add(
            expert_name="Concurrent Test", full_name="Original Name"
        )

        # Test concurrent updates
        updates = [
            experts.update(expert["id"], {"full_name": f"Update {i}"}) for i in range(5)
        ]

        results = await asyncio.gather(*updates, return_exceptions=True)
        # Verify no exceptions occurred and last update succeeded
        assert all(not isinstance(r, Exception) for r in results)

        await experts.delete(expert["id"])


if __name__ == "__main__":
    asyncio.run(TestExperts().test_concurrent_updates(experts))
# pytest tests/test_experts.py -v
