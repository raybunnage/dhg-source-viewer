from supabase import create_client
import os
from dotenv import load_dotenv


class SupabaseService:
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.client = None

    def initialize_client(self):
        """Initialize Supabase client."""
        try:
            self.client = create_client(self.url, self.key)
            return True
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            return False

    def get_test_users(self):
        """Get test users from Supabase."""
        if not self.client:
            print("Client not initialized")
            return None

        try:
            return self.client.table("test").select("*").execute()
        except Exception as e:
            print(f"Error fetching users: {e}")
            return None


def main():
    """Test the Supabase service."""

    load_dotenv()

    supabase = SupabaseService(
        url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
    )

    if supabase.initialize_client():
        print("Successfully initialized Supabase client")
        users = supabase.get_test_users()
        if users:
            print(f"Found {len(users.data)} users")
        else:
            print("No users found or error occurred")


if __name__ == "__main__":
    main()
