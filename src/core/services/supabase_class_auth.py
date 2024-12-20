import os
from dotenv import load_dotenv
from supabase import create_client


class SupabaseTest:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase = create_client(supabase_url, supabase_key)
        self.session = None

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


# Example usage
if __name__ == "__main__":
    load_dotenv()
    db = SupabaseTest(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    email = os.environ["TEST_EMAIL"]
    password = os.environ["TEST_PASSWORD"]
    print(f"email: {email}, password: {password}")
    result = db.login(email, password)
    print(f"result: {result}")
    update_result = db.update_name(2, "thinky")
    print(f"update_result: {update_result}")
    # todos = db.get_todos()
    # print(f"data: {todos}")
    db.logout()
