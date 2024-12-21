import os
from dotenv import load_dotenv
from supabase import create_client
from supabase import Client


class SupabaseService:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self._supabase = create_client(self.url, self.api_key)

    # def _initialize_client(self):
    #     self._supabase = create_client(self.url, self.api_key)

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
            print(f"Update error: {str(e)}")
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
            print(f"Login error details: {str(e)}")
            return None

    def logout(self):
        self.supabase.auth.sign_out()
        self.session = None

    def reset_password(self, email: str) -> bool:
        try:
            self.supabase.auth.api.reset_password_for_email(email)
            print(f"Password reset email sent to {email}")
            return True
        except Exception as e:
            print(f"Password reset error: {str(e)}")
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


if __name__ == "__main__":
    main()

    # def __init__(self, supabase_client: Client):
    #     if not isinstance(supabase_client, Client):
    #         raise TypeError("supabase_client must be a Supabase Client instance")
    #     self._supabase: Client = supabase_client
