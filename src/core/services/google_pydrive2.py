from pydrive2.auth import GoogleAuth
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.drive import GoogleDrive
import os
from dotenv import load_dotenv


class GooglePyDrive2:
    def __init__(self, private_key, private_key_id, client_email, client_id):
        self.private_key = private_key
        self.private_key_id = private_key_id
        self.client_email = client_email
        self.client_id = client_id
        self.drive = self._initialize_drive()

    def _initialize_drive(self):
        try:
            service_account_info = self._format_service_account_key(self.private_key)

            # Create a GoogleAuth instance
            gauth = GoogleAuth()

            # Use service account credentials
            gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                service_account_info, scopes=["https://www.googleapis.com/auth/drive"]
            )

            # Create GoogleDrive instance
            drive = GoogleDrive(gauth)

            # Test the connection
            drive.ListFile(
                {"q": "mimeType='application/vnd.google-apps.folder'"}
            ).GetList()

            return drive
        except Exception as e:
            raise Exception(f"Failed to initialize Google Drive: {str(e)}")

    def _format_service_account_key(self, private_key):
        # Ensure the private key has proper newlines
        formatted_key = private_key.replace("\\n", "\n")

        # Make sure the key has proper BEGIN/END markers if they're missing
        if not formatted_key.startswith("-----BEGIN PRIVATE KEY-----"):
            formatted_key = "-----BEGIN PRIVATE KEY-----\n" + formatted_key
        if not formatted_key.endswith("-----END PRIVATE KEY-----"):
            formatted_key = formatted_key + "\n-----END PRIVATE KEY-----\n"

        # Create the service account info dictionary
        service_account_info = {
            "type": "service_account",
            "project_id": "fabled-imagery-444902-k1",
            "private_key": formatted_key,
            "private_key_id": self.private_key_id,
            "client_email": self.client_email,
            "client_id": self.client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dhg-drive-helper%40fabled-imagery-444902-k1.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com",
        }

        return service_account_info

    def get_folders(self):
        if self.drive is None:
            raise Exception("Google Drive client not initialized properly")

        # Update the query to match the working Google API query
        file_list = self.drive.ListFile(
            {"q": "mimeType='application/vnd.google-apps.folder'"}
        ).GetList()

        if file_list:
            print("Successfully authenticated with PyDrive using the service account.")
            print(f"Found {len(file_list)} folders:")
            for file in file_list:
                print(f"- {file['title']} (ID: {file['id']})")
            return file_list  # Return the actual list instead of True
        else:
            print("Authenticated but no folders found.")
            return []  # Return empty list instead of True


    def ListFile(self):
        if self.drive is None:
            raise Exception("Google Drive client not initialized properly")

        try:
            # Query to search for mp4 files
            file_list = self.drive.ListFile({"q": "mimeType='video/mp4'"}).GetList()

            if file_list:
                return file_list
            else:
                print("No mp4 files found.")

        except Exception as e:
            print(f"Error retrieving mp4 files: {e}")


def main():
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    private_key_id = os.getenv("PRIVATE_KEY_ID")
    client_email = os.getenv("CLIENT_EMAIL")
    client_id = os.getenv("CLIENT_ID")
    drive = GooglePyDrive2(private_key, private_key_id, client_email, client_id)

    folders = drive.get_folders()
    if folders:
        print(f"Found {len(folders)} folders:")
        for folder in folders:
            print(f"- {folder['title']} (ID: {folder['id']})")
    else:
        print("No folders found or error occurred")


if __name__ == "__main__":
    main()
