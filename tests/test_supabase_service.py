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


class TestSupabaseService:
    async def test_insert_into_table(self, supabase_service):
        # Arrange
        test_data = {
            "id": str(uuid4()),
            "name": "Test Record",
            "created_at": datetime.now(),
        }

        # Act
        result = await supabase_service.insert_into_table("test_table", test_data)

        # Assert
        assert result is not None
        assert result["name"] == test_data["name"]

    async def test_select_from_table(self, supabase_service):
        # Arrange
        test_id = str(uuid4())
        where_filters = [("id", "eq", test_id)]

        # Act
        result = await supabase_service.select_from_table(
            "test_table", fields=["id", "name"], where_filters=where_filters
        )

        # Assert
        assert isinstance(result, list)

    async def test_update_table(self, supabase_service):
        # Arrange
        test_id = str(uuid4())
        update_data = {"name": "Updated Name"}
        where_filters = [("id", "eq", test_id)]

        # Act
        result = await supabase_service.update_table(
            "test_table", update_data, where_filters
        )

        # Assert
        assert result is not None
        assert result["name"] == "Updated Name"

    async def test_delete_from_table(self, supabase_service):
        # Arrange
        test_id = str(uuid4())
        where_filters = [("id", "eq", test_id)]

        # Act
        result = await supabase_service.delete_from_table("test_table", where_filters)

        # Assert
        assert result is True

    async def test_login_success(self, supabase_service):
        # Act
        result = await supabase_service.login("test@example.com", "test_password")

        # Assert
        assert result is not None
        assert hasattr(result, "session")

    async def test_login_failure(self, supabase_service):
        # Act
        result = await supabase_service.login("wrong@email.com", "wrong_password")

        # Assert
        assert result is None

    async def test_get_user(self, supabase_service):
        # Arrange
        await supabase_service.login("test@example.com", "test_password")

        # Act
        user = await supabase_service.get_user()

        # Assert
        assert user is not None
        assert user.email == "test@example.com"

    async def test_set_current_domain(self, supabase_service):
        # Arrange
        test_domain_id = str(uuid4())

        # Act
        await supabase_service.set_current_domain(test_domain_id)

        # Assert - We can verify it worked by querying a domain-scoped table
        response = await supabase_service.select_from_table(
            "some_domain_scoped_table", fields=["*"]
        )
        assert response is not None

    async def test_set_current_domain_invalid_uuid(self, supabase_service):
        # Arrange
        invalid_domain_id = "not-a-uuid"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await supabase_service.set_current_domain(invalid_domain_id)
        assert "Failed to set current domain" in str(exc_info.value)

    async def test_signup(self, supabase_service):
        # Arrange
        test_email = f"test_{uuid4()}@example.com"
        test_password = "test_password"

        # Act
        result = await supabase_service.signup(test_email, test_password)

        # Assert
        assert result is True

    async def test_reset_password(self, supabase_service):
        # Act
        result = await supabase_service.reset_password("test@example.com")

        # Assert
        assert result is True

    async def test_logout(self, supabase_service):
        # Arrange
        await supabase_service.login("test@example.com", "test_password")

        # Act
        await supabase_service.logout()

        # Assert
        assert supabase_service.session is None


if __name__ == "__main__":
    pytest.main()

# pytest tests/test_supabase_service.py
