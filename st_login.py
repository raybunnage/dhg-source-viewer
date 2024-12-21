import streamlit as st
from src.services.supabase_service import SupabaseService


def test_supabase_connection():
    st.title("Supabase Connection Test")

    # Initialize session state variables if they don't exist
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Initialize SupabaseTest instance
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    # st.write(f"URL: {url}, Key: {key}")

    if "supabase" not in st.session_state or st.session_state.supabase is None:
        st.session_state.supabase = SupabaseService(url, key)

    # Login Section
    st.header("Login")

    # Only show the login form if not authenticated
    if not st.session_state.authenticated:
        # Create login form
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    try:
                        st.write("Attempting login...")
                        auth_response = st.session_state.supabase.login(email, password)

                        if auth_response and auth_response.user:
                            st.session_state.auth_session = auth_response
                            st.session_state.authenticated = True
                            st.success(
                                f"Login successful! Welcome, {auth_response.user.email}"
                            )
                            st.rerun()  # Rerun to update the UI
                        else:
                            st.error("Login failed: Invalid credentials")
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")

    # Show login status
    if st.session_state.authenticated:
        st.info("You are currently logged in")

    # Update Name Section
    st.header("Update Name Test")
    update_id = st.number_input("Enter ID to update", min_value=1, step=1)
    new_name = st.text_input("Enter new name")

    if st.button("Update Name"):
        if not st.session_state.authenticated:
            st.error("Please login first")
            return
        if update_id and new_name:
            try:
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
        if not st.session_state.authenticated:
            st.error("Please login first")
            return
        todos = st.session_state.supabase.get_todos()
        st.json(todos)

    # Fetch Users Section
    st.header("Fetch Users Test")
    if st.button("Get Users"):
        if not st.session_state.authenticated:
            st.error("Please login first")
            return
        try:
            users = st.session_state.supabase.get_test_users()
            if users:
                st.success(f"Found {len(users.data)} users")
                st.json(users.data)
            else:
                st.error("No users found or error occurred")
        except Exception as e:
            st.error(f"Failed to fetch users: {str(e)}")

    # Logout Section
    st.header("Logout Test")
    if st.button("Logout"):
        st.session_state.supabase.logout()
        # Clear authentication state but keep supabase instance
        st.session_state.authenticated = False
        if "auth_session" in st.session_state:
            del st.session_state.auth_session
        st.success("Logged out successfully!")
        st.rerun()  # Rerun to update the UI and show the login form again


if __name__ == "__main__":
    test_supabase_connection()

# streamlit run st_login.py
