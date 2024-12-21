from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleDriveService:
    def __init__(self, credentials):
        self.credentials = credentials
        self.service = None

    def format_service_account_key(self, private_key):
        """Format a service account configuration with proper private key formatting."""
        formatted_key = private_key.replace("\\n", "\n")
        if not formatted_key.startswith("-----BEGIN PRIVATE KEY-----"):
            formatted_key = "-----BEGIN PRIVATE KEY-----\n" + formatted_key
        if not formatted_key.endswith("-----END PRIVATE KEY-----"):
            formatted_key = formatted_key + "\n-----END PRIVATE KEY-----\n"
        
        return {
            "type": "service_account",
            "project_id": self.credentials["project_id"],
            "private_key": formatted_key,
            "private_key_id": self.credentials["private_key_id"],
            "client_email": self.credentials["client_email"],
            "client_id": self.credentials["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": self.credentials["client_x509_cert_url"],
            "universe_domain": "googleapis.com",
        }

    def initialize_service(self):
        """Initialize Google Drive service."""
        try:
            service_account_info = self.format_service_account_key(self.credentials["private_key"])
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=["https://www.googleapis.com/auth/drive"],
            )
            self.service = build("drive", "v3", credentials=credentials)
            return True
        except ValueError as e:
            print(f"Error creating credentials: {e}")
            return False

    def get_first_mp4(self):
        """Get the first MP4 file from Drive."""
        if not self.service:
            print("Service not initialized")
            return None

        try:
            results = self.service.files().list(
                q="mimeType='video/mp4'",
                fields="files(id, name)",
                pageSize=1
            ).execute()

            files = results.get('files', [])
            return files[0] if files else None
        except Exception as e:
            print(f"Error retrieving mp4 files: {e}")
            return None

def main():
    """Test the Google Drive service."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    credentials = {
        "project_id": os.getenv("PROJECT_ID"),
        "private_key": os.getenv("PRIVATE_KEY"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL")
    }
    
    drive_service = GoogleDriveService(credentials)
    if drive_service.initialize_service():
        print("Successfully initialized Drive service")
        video = drive_service.get_first_mp4()
        if video:
            print(f"Found video: {video['name']}")
        else:
            print("No MP4 files found")

if __name__ == "__main__":
    main() 