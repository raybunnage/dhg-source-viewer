import streamlit as st
from supabase import create_client

import streamlit as st
from src.auth import authenticate_user
from src.database import get_folders, get_files
from src.utils import setup_page

from dotenv import load_dotenv

from src.database import test_supabase_connection


# load_dotenv()

# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def st_manage_supabase():
    st.set_page_config(layout="wide")
    st.title("Supabase Connection Test")

    api_key = st.secrets["SUPABASE_KEY"]
    url_key = st.secrets["SUPABASE_URL"]

    # st.write(api_key)
    # st.write(url_key)

    supabase = create_client(url_key, api_key)

    users = supabase.table("test").select("*").execute()
    st.write(f"Number of users: {len(users.data)}")

    # st.write(users)


# def st_supa():
#     st.set_page_config(layout="wide")
#     st.title("Supabase Connection Test")

#     users = test_supabase_connection()

#     # Debug print to see the structure
#     # st.write("Debug - Users data:", users.data)

#     # Then use the correct key from what you see in the debug output
#     # For example, if the key is "username" instead of "name":
#     user_list = [user["username"] for user in users.data]  # Adjust the key as needed

#     selected_user = st.selectbox("Select a User", user_list)
#     st.write(f"Selected User: {selected_user}")


# def authenticate_user():
#     """Handle user authentication"""
#     if "authenticated" not in st.session_state:
#         st.session_state.authenticated = False

#     if not st.session_state.authenticated:
#         with st.form("login_form"):
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             submit = st.form_submit_button("Login")

#             if submit:
#                 try:
#                     response = supabase.auth.sign_in_with_password(
#                         {"email": email, "password": password}
#                     )
#                     st.session_state.authenticated = True
#                     st.session_state.user = response.user
#                     return True
#                 except Exception as e:
#                     st.error("Invalid credentials")
#                     return False
#         return False
#     return True


def main():
    setup_page()

    # Authentication
    # if not authenticate_user():
    #     st.warning("Please log in to access the file viewer.")
    #     return

    # Sidebar navigation
    st.sidebar.title("Navigation")
    selected_folder = st.sidebar.selectbox("Select Folder", get_folders())

    # Main content
    st.title("DHG Source Viewer")

    if selected_folder:
        files = get_files(selected_folder)
        if files:
            for file in files:
                st.write(f"📄 {file['name']}")
        else:
            st.info("No files found in this folder")


if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     st_manage_supabase()

# streamlit run streamlit_app.py
