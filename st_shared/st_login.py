import streamlit as st
from pathlib import Path
import sys
# Set page config before any other Streamlit commands
# st.set_page_config(layout="wide")

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
from st_shared.streamlit_base import StreamlitBase
from src.services.supabase_service import SupabaseService


class AsyncLoginConnection:
    def __init__(self):
        self.client = None
        self._initialized = False

    async def initialize(self):
        """Initialize the Supabase connection"""
        if not self._initialized:
            try:
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                supabase = SupabaseService(url, key)
                email = st.secrets["TEST_EMAIL"]
                password = st.secrets["TEST_PASSWORD"]

                await supabase.login(email, password)
                self._initialized = True
                st.session_state.app_state.is_initialized = True
            except Exception as e:
                raise Exception(f"Failed to initialize Supabase connection: {e}")

    async def get_client(self):
        """Get the initialized client, initializing if necessary"""
        if not self._initialized:
            await self.initialize()
        return self.client


class LoginManager(StreamlitBase):
    def __init__(self):
        super().__init__("login_manager")
        self.connection = self._get_connection()

    @staticmethod
    @st.cache_resource
    def _get_connection():
        """Cache the connection instance"""
        return AsyncLoginConnection()

    def _validate_data(self, data):
        """Implement the abstract method from BaseDB"""
        # Basic validation - check if data is a dict and not empty
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        if not data:
            raise ValueError("Data cannot be empty")
        return True

    def render_signup(self):
        st.subheader("Signup")

    def render_login(self):
        st.subheader("Login")

    def render_reset_password(self):
        st.subheader("Reset Password")

    def render_logout(self):
        st.subheader("Logout")

    def main(self, set_page_config: bool = False):
        # Initialize connection
        if not st.session_state.app_state.is_initialized:
            try:
                self.run_async(self.connection.initialize())
            except Exception as e:
                self.set_error(str(e))

        # Show any errors
        self.show_error()

        # Create two columns
        col1, col2 = st.columns(2)

        with col1:
            st.sidebar.title("Manage Experts")
            st.sidebar.subheader("Actions")
            action = st.sidebar.radio(
                "Select Action", ["Signup", "Login", "Reset Password", "Logout"]
            )

            if action == "Signup":
                self.render_signup()
            elif action == "Login":
                self.render_login()
            elif action == "Reset Password":
                self.render_reset_password()
            elif action == "Logout":
                self.render_logout()


if __name__ == "__main__":
    app = LoginManager()
    app.main()

    # Sign Up Section
    # st.header("Sign Up")
    # if not st.session_state.authenticated:
    #     with st.form("signup_form"):
    #         signup_email = st.text_input("Email", key="signup_email")
    #         signup_password = st.text_input("Password", type="password", key="signup_password")
    #         signup_button = st.form_submit_button("Sign Up")

    #         if signup_button:
    #             if not signup_email or not signup_password:
    #                 st.error("Please enter both email and password")
    #             else:
    #                 try:
    #                     st.write("Attempting signup...")
    #                     signup_response = st.session_state.supabase.signup(signup_email, signup_password)

    #                     if signup_response and signup_response.user:
    #                         st.success("Sign up successful! Please check your email to confirm your account.")
    #                     else:
    #                         st.error("Sign up failed")
    #                 except Exception as e:
    #                     st.error(f"Sign up failed: {str(e)}")


#     # Only show the login form if not authenticated
#     if not st.session_state.authenticated:
#         # Create login form
#         with st.form("login_form"):
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             submit_button = st.form_submit_button("Login")

#             if submit_button:
#                 if not email or not password:
#                     st.error("Please enter both email and password")
#                 else:
#                     try:
#                         st.write("Attempting login...")
#                         auth_response = st.session_state.supabase.login(email, password)

#                         if auth_response and auth_response.user:
#                             st.session_state.auth_session = auth_response
#                             st.session_state.authenticated = True
#                             st.success(
#                                 f"Login successful! Welcome, {auth_response.user.email}"
#                             )
#                             st.rerun()  # Rerun to update the UI
#                         else:
#                             st.error("Login failed: Invalid credentials")
#                     except Exception as e:
#                         st.error(f"Login failed: {str(e)}")

#     # Show login status
#     if st.session_state.authenticated:
#         st.info("You are currently logged in")

#     # Update Name Section
#     st.header("Update Name Test")
#     update_id = st.number_input("Enter ID to update", min_value=1, step=1)
#     new_name = st.text_input("Enter new name")

#     if st.button("Update Name"):
#         if not st.session_state.authenticated:
#             st.error("Please login first")
#             return
#         if update_id and new_name:
#             try:
#                 update_result = st.session_state.supabase.update_name(
#                     update_id, new_name
#                 )
#                 if update_result:
#                     st.success(f"Successfully updated ID {update_id} to '{new_name}'")
#                 else:
#                     st.error(f"Failed to update ID {update_id}")
#             except Exception as e:
#                 st.error(f"Update failed: {str(e)}")
#         else:
#             st.error("Please enter both ID and new name")

#     # Fetch Todos Section
#     st.header("Fetch Todos Test")
#     if st.button("Get Todos"):
#         if not st.session_state.authenticated:
#             st.error("Please login first")
#             return
#         todos = st.session_state.supabase.get_todos()
#         st.json(todos)

#     # Fetch Users Section
#     st.header("Fetch Users Test")
#     if st.button("Get Users"):
#         if not st.session_state.authenticated:
#             st.error("Please login first")
#             return
#         try:
#             users = st.session_state.supabase.get_test_users()
#             if users:
#                 st.success(f"Found {len(users.data)} users")
#                 st.json(users.data)
#             else:
#                 st.error("No users found or error occurred")
#         except Exception as e:
#             st.error(f"Failed to fetch users: {str(e)}")

#     # Logout Section
#     st.header("Logout Test")
#     if st.button("Logout"):
#         st.session_state.supabase.logout()
#         # Clear authentication state but keep supabase instance
#         st.session_state.authenticated = False
#         if "auth_session" in st.session_state:
#             del st.session_state.auth_session
#         st.success("Logged out successfully!")
#         st.rerun()  # Rerun to update the UI and show the login form again


# if __name__ == "__main__":
#     test_supabase_connection()

# streamlit run st_shared/st_login.py
