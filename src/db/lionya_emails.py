import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.services.supabase_service import SupabaseService


class LionyaEmails:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def say_hello_world(self):
        print("Hello, World!")

if __name__ == "__main__":
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase_client = SupabaseService(supabase_url, supabase_key)
    lionya_emails = LionyaEmails(supabase_client)
    lionya_emails.say_hello_world()