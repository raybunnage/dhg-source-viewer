import streamlit as st
import os
from src.core.services.supabase_class_auth import SupabaseTest


def test_supabase_connection():
    st.title("Supabase Connection Test")

    # Initialize SupabaseTest instance
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    st.write(f"URL: {url}, Key: {key}")

    if "supabase" not in st.session_state:
        st.session_state.supabase = SupabaseTest(url, key)

    # Login Section
    st.header("Login Test")
    email = st.secrets["TEST_EMAIL"]
    password = st.secrets["TEST_PASSWORD"]
    st.write(f"Email: {email}, Password: {password}")

    if st.button("Login"):
        try:
            st.write("Attempting login...")
            st.write(f"Using URL: {url}")  # Debug line (will be hidden in production)
            auth_response = st.session_state.supabase.login(email, password)

            st.write("Auth response type:", type(auth_response))  # Debug line
            st.write("Raw auth response:", auth_response)  # Debug line

            if auth_response:
                st.write("Has auth response")  # Debug line
                st.write(
                    "User data:", getattr(auth_response, "user", None)
                )  # Debug line

            if auth_response and auth_response.user:
                st.session_state.auth_session = auth_response
                st.success("Login successful!")
            else:
                st.error("Login failed: Invalid credentials or no user data received")
                st.write(
                    "Please check your SUPABASE_URL, SUPABASE_KEY, TEST_EMAIL, and TEST_PASSWORD in your secrets"
                )
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            st.write("Full error details:", e)  # Temporary debug line

    # Update Name Section
    st.header("Update Name Test")
    update_id = st.number_input("Enter ID to update", min_value=1, step=1)
    new_name = st.text_input("Enter new name")

    if st.button("Update Name"):
        if update_id and new_name:
            try:
                # Check if user is authenticated
                if not st.session_state.get("auth_session"):
                    st.error("Please login first")
                    return
                update_result = st.session_state.supabase.update_name(
                    update_id, new_name
                )
                if update_result:
                    st.success(f"Successfully updated ID {update_id} to '{new_name}'")
                else:
                    st.error(f"Failed to update ID {update_id}")
            except Exception as e:
                st.error(f"Update failed: {str(e)}")
        else:
            st.error("Please enter both ID and new name")

    # Fetch Todos Section
    st.header("Fetch Todos Test")
    if st.button("Get Todos"):
        todos = st.session_state.supabase.get_todos()
        st.json(todos)

    # Logout Section
    st.header("Logout Test")
    if st.button("Logout"):
        st.session_state.supabase.logout()
        st.success("Logged out successfully!")


if __name__ == "__main__":
    test_supabase_connection()

# streamlit run st_login.py
