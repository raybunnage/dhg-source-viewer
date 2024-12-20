# Try this instead of your current import
import os.path
import sys
import asyncio
# project_root = os.path.dirname(
#     os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# )
# project_root = str(Path(__file__).parent.parent.parent.parent)
# sys.path.append(project_root)
# print(f"project_root: {project_root}")
# print(f"sys.path: {sys.path}")

# from src.core.services.supabase_client import SupabaseService

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
from src.core.services.supabase_client import SupabaseService
from supabase import Client
from typing import Optional
import os
from dotenv import load_dotenv
import streamlit as st
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class AuthResponse:
    """Custom AuthResponse class for Streamlit-Supabase integration"""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    user: Optional[Dict] = None
    session: Optional[Dict] = None
    needs_email_confirmation: bool = False


class SupabaseAuth:
    def __init__(self, supabase_client: Client):
        if not isinstance(supabase_client, Client):
            raise TypeError("supabase_client must be a Supabase Client instance")
        self._supabase: Client = supabase_client

    @property
    def supabase(self) -> Client:
        """Ensure we always have a valid Supabase client."""
        if not hasattr(self, "_supabase") or not isinstance(self._supabase, Client):
            raise RuntimeError("Supabase client not properly initialized")
        return self._supabase

    def login(self, email: str, password: str) -> bool:
        """Authenticate user with email and password."""
        if not email or not password:
            st.error("Email and password are required")
            return False

        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response and response.user:
                st.session_state["user"] = response.user
                return True
            return False
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False

    def signup(self, email: str, password: str) -> bool:
        """Register a new user."""
        try:
            response = self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )
            st.session_state["user"] = response.user
            return True
        except Exception as e:
            st.error(f"Signup failed: {str(e)}")
            return False

    def logout(self) -> None:
        """Sign out the current user."""
        try:
            self.supabase.auth.sign_out()
            if "user" in st.session_state:
                del st.session_state["user"]
        except Exception as e:
            st.error(f"Logout failed: {str(e)}")

    def get_current_user(self) -> Optional[dict]:
        """Get the current authenticated user."""
        return st.session_state.get("user")

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return "user" in st.session_state

    async def sign_up_with_email(self, email: str, password: str) -> AuthResponse:
        """
        Register a new user with email and password.
        """
        try:
            data = await self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )

            if data.error:
                return AuthResponse(success=False, error=str(data.error))

            # Check if email confirmation is needed
            if not data.user.identities:
                return AuthResponse(
                    success=True,
                    message="Please check your email for confirmation link",
                    needs_email_confirmation=True,
                )

            return AuthResponse(
                success=True, user=data.user, needs_email_confirmation=False
            )

        except Exception as e:
            return AuthResponse(success=False, error=str(e))

    def test_supabase_auth(self):
        """Test the SupabaseAuth class functionality."""

        email = "bunnage.ray@gmail.com"
        password = "ab13!D1#Go0d"
        signup_success = self.signup(email, password)
        print(f"Signup success: {signup_success}")

        # Test login
        login_success = self.login(email, password)
        print(f"Login success: {login_success}")

        # Test get_current_user
        current_user = self.get_current_user()
        print(f"Current user: {current_user}")

        # Test is_authenticated
        is_auth = self.is_authenticated()
        print(f"Is authenticated: {is_auth}")

        # Test logout
        self.logout()
        is_auth_after_logout = self.is_authenticated()
        print(f"Is authenticated after logout: {is_auth_after_logout}")


def test_test_supabase_auth():
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase = SupabaseService(supabase_url, supabase_key)
    supabase.initialize_client()
    auth = SupabaseAuth(supabase.client)
    # auth.test_supabase_auth()
    auth.sign_up_with_email("bunnage.ray@gmail.com", "ab13!D1#Go0d")


if __name__ == "__main__":
    test_test_supabase_auth()
