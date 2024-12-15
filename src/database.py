from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def get_folders():
    """Fetch available folders from Supabase"""
    try:
        response = supabase.table('folders').select("*").execute()
        return [folder['name'] for folder in response.data]
    except Exception as e:
        print(f"Error fetching folders: {e}")
        return []

def get_files(folder_name):
    """Fetch files for a specific folder from Supabase"""
    try:
        response = supabase.table('files')\
            .select("*")\
            .eq('folder_name', folder_name)\
            .execute()
        return response.data
    except Exception as e:
        print(f"Error fetching files: {e}")
        return []