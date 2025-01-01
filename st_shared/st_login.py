import streamlit as st
from pathlib import Path
import sys
import logging
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
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize the Supabase connection"""
        if not self._initialized:
            try:
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                self.logger.debug(f"Initializing with URL: {url[:10]}...")
                supabase = SupabaseService(url, key)
                email = st.secrets["TEST_EMAIL"]
                password = st.secrets["TEST_PASSWORD"]
                login_result = await supabase.login(email, password)
                self.logger.debug(f"Happy Initial login result: {login_result}")
                self._initialized = True
                self.client = supabase
                st.session_state.app_state.is_initialized = True
            except Exception as e:
                self.logger.error(f"Failed to initialize Supabase connection: {e}")
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

    async def do_signup(self, email: str, password: str):
        """Attempt to sign up a new user"""
        try:
            client = await self.connection.get_client()
            success = await client.signup(email, password)
            if success:
                self.logger.info(f"Successfully signed up user with email: {email}")
            else:
                self.logger.warning(f"Signup failed for email: {email}")
            return success
        except Exception as e:
            self.logger.error(f"Error during signup for {email}: {str(e)}")
            self.set_error(f"Signup failed: {str(e)}")
            return False

    async def do_login(self, email: str, password: str):
        """Attempt to login a user"""
        try:
            client = await self.connection.get_client()
            self.logger.debug(f"Got client: {client}")
            result = await client.login(email, password)
            self.logger.debug(f"Login result: {result}")
            if result:
                self.logger.info(f"Successfully logged in user with email: {email}")
                return True
            else:
                self.logger.warning(f"Login failed for email: {email}")
                return False
        except Exception as e:
            self.logger.error(f"Error during login for {email}: {str(e)}")
            self.set_error(f"Login failed: {str(e)}")
            return False

    async def do_reset_password(self, email: str):
        """Attempt to reset a user's password by sending reset email"""
        try:
            if not email:
                self.logger.warning("Reset password failed: No email provided")
                return False

            client = await self.connection.get_client()
            # Call the SupabaseService reset_password_for_email method
            result = await client.reset_password_for_email(email)

            if result:
                self.logger.info(f"Successfully sent password reset email to: {email}")
                return True
            else:
                self.logger.warning(f"Failed to send password reset email to: {email}")
                return False

        except Exception as e:
            self.logger.error(f"Error during password reset for {email}: {str(e)}")
            self.set_error(f"Password reset failed: {str(e)}")
            return False

    async def do_logout(self):
        """Attempt to logout a user"""
        try:
            client = await self.connection.get_client()
            if client is None:
                self.logger.error("Cannot logout - client is None")
                return False

            # The SupabaseService logout() method always returns None
            # So we don't need to check its return value
            await client.logout()
            self.logger.info("Successfully logged out user")
            return True
        except Exception as e:
            self.logger.error(f"Error during logout: {str(e)}")
            self.set_error(f"Logout failed: {str(e)}")
            return False

    def render_signup(self):
        self.logger.debug("Rendering signup form")
        st.subheader("Signup")
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            submitted = st.form_submit_button("Sign Up")

            if submitted:
                self.logger.info(f"Signup form submitted for email: {email}")

                if password != confirm_password:
                    self.logger.warning("Signup failed: Passwords do not match")
                    st.error("Passwords do not match")
                    return

                if not email or not password:
                    self.logger.warning("Signup failed: Missing required fields")
                    st.error("Please fill in all fields")
                    return

                try:
                    self.logger.info(f"Attempting signup for email: {email}")
                    success = self.run_async(self.do_signup(email, password))
                    if success:
                        self.logger.info(f"Signup successful for email: {email}")
                        st.success(
                            "Signup successful! Please check your email to confirm your account."
                        )
                    else:
                        self.logger.error(f"Signup failed for email: {email}")
                        st.error("Signup failed")
                except Exception as e:
                    self.logger.error(f"Error during signup for {email}: {str(e)}")
                    st.error(f"Error during signup: {str(e)}")

    def render_login(self):
        st.subheader("Login")
        self.logger.debug("Rendering login form")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Login")

            if submitted:
                self.logger.info(f"Login form submitted for email: {email}")

                if not email or not password:
                    self.logger.warning("Login failed: Missing required fields")
                    st.error("Please fill in all fields")
                    return

                try:
                    self.logger.info(f"Attempting login for email: {email}")
                    success = self.run_async(self.do_login(email, password))
                    if success:
                        self.logger.info(f"Login successful for email: {email}")
                        st.success(f"Login successful! Welcome, {email}")
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        self.logger.error(f"Login failed for email: {email}")
                        st.error("Invalid email or password")
                except Exception as e:
                    self.logger.error(f"Error during login for {email}: {str(e)}")
                    st.error(f"Error during login: {str(e)}")

    def render_reset_password(self):
        st.subheader("Reset Password")
        self.logger.debug("Rendering reset password form")
        with st.form("reset_password_form"):
            email = st.text_input("Email")

            submitted = st.form_submit_button("Reset Password")

            if submitted:
                self.logger.info(f"Reset password form submitted for email: {email}")

                if not email:
                    self.logger.warning(
                        "Reset password failed: Missing required fields"
                    )
                    st.error("Please fill in all fields")
                    return

                try:
                    self.logger.info(f"Attempting reset password for email: {email}")
                    success = self.run_async(self.do_reset_password(email))
                    if success:
                        self.logger.info(
                            f"Reset password successful for email: {email}"
                        )
                        st.success(
                            f"Reset password successful! Please check your email for instructions."
                        )
                        st.rerun()
                    else:
                        self.logger.error(f"Reset password failed for email: {email}")
                        st.error("Failed to send reset password email")
                except Exception as e:
                    self.logger.error(
                        f"Error during reset password for {email}: {str(e)}"
                    )
                    st.error(f"Error during reset password: {str(e)}")

    def render_logout(self):
        st.subheader("Logout")
        self.logger.info("Attempting logout")
        try:
            client = self.run_async(self.connection.get_client())
            if client:
                success = self.run_async(self.do_logout())
                if success:
                    self.logger.info("Logout successful")
                    st.success("You have been logged out successfully")
                    st.session_state.authenticated = False
                    st.rerun()
                else:
                    self.logger.error("Logout failed")
                    st.error("Failed to logout")
            else:
                self.logger.error("Logout failed: No client connection")
                st.error("Failed to logout - no connection")
        except Exception as e:
            self.logger.error(f"Logout failed: {str(e)}")
            st.error(f"Failed to logout: {str(e)}")

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
