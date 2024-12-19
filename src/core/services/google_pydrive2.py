from pydrive2.auth import GoogleAuth
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.drive import GoogleDrive
import json

class GooglePyDrive2:
    def __init__(self, credentials_path="client_secrets.json"):
        self.credentials_path = credentials_path
        self.drive = self._initialize_drive()

    def _initialize_drive(self):
        """Initialize PyDrive2 with service account credentials"""
        try:
            service_account_info = self._get_service_account_info()
            if not service_account_info:
                return None

            # Create a GoogleAuth instance
            gauth = GoogleAuth()

            # Use service account credentials
            gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                service_account_info, 
                scopes=["https://www.googleapis.com/auth/drive"]
            )

            # Create GoogleDrive instance
            return GoogleDrive(gauth)

        except Exception as e:
            print(f"Error initializing PyDrive2: {e}")
            return None

    def _get_service_account_info(self):
        """Read service account information from JSON file"""
        try:
            with open(self.credentials_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading service account info: {e}")
            return None

    def list_folders(self):
        """List all folders in Google Drive"""
        if not self.drive:
            print("Drive not initialized")
            return []

        try:
            file_list = self.drive.ListFile({
                "q": "mimeType='application/vnd.google-apps.folder'"
            }).GetList()

            folders = []
            for file in file_list:
                folders.append({
                    "title": file["title"],
                    "id": file["id"]
                })
            return folders

        except Exception as e:
            print(f"Error listing folders: {e}")
            return []


if __name__ == "__main__":
    drive = GooglePyDrive2()
    print(drive.list_folders())
