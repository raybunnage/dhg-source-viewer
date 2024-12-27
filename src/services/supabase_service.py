import os
from dotenv import load_dotenv
from supabase import create_client
from supabase import Client
from src.db.base_db import BaseDB


class SupabaseService(BaseDB):
    def __init__(self, url, api_key):
        super().__init__()
        self.url = url
        self.api_key = api_key
        self._supabase = create_client(self.url, self.api_key)

    @property
    def supabase(self) -> Client:
        """Ensure we always have a valid Supabase client."""
        if not hasattr(self, "_supabase") or not isinstance(self._supabase, Client):
            raise RuntimeError("Supabase client not properly initialized")
        return self._supabase

    def get_test_users(self):
        # The client automatically handles authentication after login
        return self.supabase.table("test").select("*").execute()

    def get_todos(self):
        data = self.supabase.table("todos").select("*").execute()
        return data

    def select_from_table(
        self, table_name: str, fields: dict, where_filters: list = None
    ):
        try:
            if fields == "*":
                query = self.supabase.table(table_name).select("*")
            else:
                query = self.supabase.table(table_name).select(",".join(fields))

            if where_filters:
                for filter in where_filters:
                    column, operator, value = filter
                    if operator == "eq":
                        query = query.eq(column, value)
                    elif operator == "neq":
                        query = query.neq(column, value)
                    elif operator == "lt":
                        query = query.lt(column, value)
                    elif operator == "lte":
                        query = query.lte(column, value)
                    elif operator == "gt":
                        query = query.gt(column, value)
                    elif operator == "gte":
                        query = query.gte(column, value)
                    elif operator == "like":
                        query = query.like(column, value)
                    elif operator == "ilike":
                        query = query.ilike(column, value)
                    elif operator == "is":
                        query = query.is_(column, value)
                    elif operator == "in":
                        query = query.in_(column, value)
                    elif operator == "contains":
                        query = query.contains(column, value)
                    elif operator == "contained_by":
                        query = query.contained_by(column, value)
                    elif operator == "range_lt":
                        query = query.range_lt(column, value)
                    elif operator == "range_lte":
                        query = query.range_lte(column, value)
                    elif operator == "range_gt":
                        query = query.range_gt(column, value)
                    elif operator == "range_gte":
                        query = query.range_gte(column, value)
                    elif operator == "range_adjacent":
                        query = query.range_adjacent(column, value)
                    elif operator == "overlaps":
                        query = query.overlaps(column, value)
                    elif operator == "text_search":
                        query = query.text_search(column, value)
                    else:
                        raise ValueError(f"Unsupported operator: {operator}")

            response = query.execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Select error: {str(e)}")
            return None

    def update_table(
        self, table_name: str, update_fields: dict, where_filters: list
    ) -> dict | None:
        """Update records matching the filter and return the updated record.
        Returns:
            dict | None: The updated record with all fields, or None if update failed
        """
        try:
            query = self.supabase.table(table_name).update(update_fields)

            if where_filters:
                for filter in where_filters:
                    column, operator, value = filter
                    if operator == "eq":
                        query = query.eq(column, value)
                    elif operator == "neq":
                        query = query.neq(column, value)
                    elif operator == "lt":
                        query = query.lt(column, value)
                    elif operator == "lte":
                        query = query.lte(column, value)
                    elif operator == "gt":
                        query = query.gt(column, value)
                    elif operator == "gte":
                        query = query.gte(column, value)
                    elif operator == "like":
                        query = query.like(column, value)
                    elif operator == "ilike":
                        query = query.ilike(column, value)
                    elif operator == "is":
                        query = query.is_(column, value)
                    elif operator == "in":
                        query = query.in_(column, value)
                    elif operator == "contains":
                        query = query.contains(column, value)
                    elif operator == "contained_by":
                        query = query.contained_by(column, value)
                    elif operator == "range_lt":
                        query = query.range_lt(column, value)
                    elif operator == "range_lte":
                        query = query.range_lte(column, value)
                    elif operator == "range_gt":
                        query = query.range_gt(column, value)
                    elif operator == "range_gte":
                        query = query.range_gte(column, value)
                    elif operator == "range_adjacent":
                        query = query.range_adjacent(column, value)
                    elif operator == "overlaps":
                        query = query.overlaps(column, value)
                    elif operator == "text_search":
                        query = query.text_search(column, value)
                    else:
                        raise ValueError(f"Unsupported operator: {operator}")

            response = query.execute()
            if response.data and len(response.data) > 0:
                return response.data[0]  # Return first updated record
            return None
        except Exception as e:
            self.logger.error(f"Update error: {str(e)}")
            return None

    def insert_into_table(
        self, table_name: str, insert_fields: dict, upsert: bool = False
    ) -> dict | None:
        """Insert a record and return the created record or None if failed.
        Args:
            table_name: The table to insert into
            insert_fields: The fields to insert
            upsert: If True, update existing record instead of failing on conflict
        Returns:
            dict | None: The newly created/updated record with all fields including id, or None if failed
        """
        try:
            query = self.supabase.table(table_name)
            if upsert:
                # Use upsert operation - will update if exists, insert if not
                response = query.upsert(insert_fields).execute()
            else:
                # Regular insert - will fail if record exists
                response = query.insert(insert_fields).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"Insert error: {str(e)}")
            return None

    def update_name(self, id: int, new_name: str) -> bool:
        try:
            response = (
                self.supabase.table("todos")
                .update({"name": new_name})
                .eq("id", id)
                .execute()
            )
            # Check if any rows were affected by the update
            if response.data and len(response.data) > 0:
                print(f"Successfully updated todo {id} to '{new_name}'")
                return True
            else:
                print(f"No todo found with id {id} or policy prevented update")
                return False
        except Exception as e:
            self.logger.error(f"Update error: {str(e)}")
            return False

    def set_email_and_password(self, email: str, password: str):
        self.email = email
        self.password = password

    def login(self, email: str, password: str):
        try:
            self.email = email
            self.password = password
            print(f"Attempting login with email: {email}")
            data = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            print(f"Auth response data: {data}")
            print(f"User data: {data.user if data else 'No data'}")
            self.session = data
            return data
        except Exception as e:
            self.logger.error(f"Login error details: {str(e)}")
            return None

    def logout(self):
        self.supabase.auth.sign_out()
        self.session = None

    def reset_password(self, email: str) -> bool:
        try:
            self.supabase.auth.api.reset_password_for_email(email)
            self.logger.error(f"Password reset email sent to {email}")
            return True
        except Exception as e:
            self.logger.error(f"Password reset error: {str(e)}")
            return False

    def delete_from_table(self, table_name: str, where_filters: list) -> bool:
        """Delete records matching the filter.
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            query = self.supabase.table(table_name).delete()
            # Apply filters
            for column, operator, value in where_filters:
                if operator == "eq":
                    query = query.eq(column, value)
                # ... other operators ...

            response = query.execute()
            return bool(response.data)  # True if any rows were deleted
        except Exception as e:
            self.logger.error(f"Delete error: {str(e)}")
            return False


def main():
    """Test the Supabase service."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    # Then create the service with the client
    todos = supabase.get_todos()
    if todos:
        print(f"Found {len(todos.data)} todos")
    else:
        print("No todos found or error occurred")

    users = supabase.get_test_users()
    if users:
        print(f"Found {len(users.data)} users")
    else:
        print("No users found or error occurred")


def update_document_type_description():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)

    try:
        response = supabase.update_table(
            "uni_document_types",
            {"description": "includes master's thesis"},
            [("document_type", "eq", "thesis")],
        )
        if response.status_code == 200:
            print("Document type description updated successfully.")
        else:
            print(
                f"Failed to update document type description. Status code: {response.status_code}"
            )
    except Exception as e:
        print(f"Error updating document type description: {str(e)}")


def insert_test():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)

    new_expert = {
        "expert_name": "John Doe",
        "full_name": "Johnathan Doe",
        "starting_ref_id": 123,
        "expertise_area": "AI",
        "experience_years": 5,
        "user_id": "f5972054-059e-4b1e-915e-268bcdcc94b9",
    }
    try:
        response = supabase.insert_into_table("experts", new_expert)
        if response:  # If we got back a dict with the inserted data
            print("New expert inserted successfully.")
            print(f"Inserted expert data: {response}")
        else:
            print("Failed to insert new expert.")
    except Exception as e:
        print(f"Error inserting new expert: {str(e)}")


def select_from_table():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = SupabaseService(url, key)
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    supabase.login(email, password)
    data = supabase.select_from_table(
        "uni_document_types",
        [
            "document_type",
            "description",
            "is_ai_generated",
            "mime_type",
            "file_extension",
            "category",
        ],
        [("is_active", "eq", True)],
    )
    print(data)
    fields = "*"
    expert_id = "34acaa61-7fb4-4c02-b463-a55128e354f3"
    data = supabase.select_from_table(
        "experts",
        fields,
        [("id", "eq", expert_id)],
    )
    print(data)


if __name__ == "__main__":
    select_from_table()

    # def __init__(self, supabase_client: Client):
    #     if not isinstance(supabase_client, Client):
    #         raise TypeError("supabase_client must be a Supabase Client instance")
    #     self._supabase: Client = supabase_client
