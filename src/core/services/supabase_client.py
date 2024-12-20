from supabase import create_client
import os
from dotenv import load_dotenv


class SupabaseService:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.client = None

    def initialize_client(self):
        self.client = create_client(self.url, self.api_key)
        
    def get_test_users(self):
        # Get the session from the client
        session = self.client.auth.get_session()
        
        # Include the session token in the request
        return self.client.table('test_users').select("*").execute(
            headers={
                'Authorization': f'Bearer {session.access_token}'
            }
        )


def main():
    """Test the Supabase service."""

    load_dotenv()

    supabase = SupabaseService(
        url=os.getenv("SUPABASE_URL"), api_key=os.getenv("SUPABASE_KEY")
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
