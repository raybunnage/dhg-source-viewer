import streamlit as st
from src.core.services.google_drive import GoogleDriveService
from src.core.services.supabase_client import SupabaseService

def get_drive_service():
    """Get Google Drive service with Streamlit secrets."""
    credentials = {
        "project_id": "fabled-imagery-444902-k1",
        "private_key": st.secrets["PRIVATE_KEY"],
        "private_key_id": st.secrets["PRIVATE_KEY_ID"],
        "client_email": st.secrets["CLIENT_EMAIL"],
        "client_id": st.secrets["CLIENT_ID"],
        "client_x509_cert_url": st.secrets["CLIENT_X509_CERT_URL"]
    }
    
    drive_service = GoogleDriveService(credentials)
    if not drive_service.initialize_service():
        st.error("Failed to initialize Drive service")
        return None
    return drive_service

def get_supabase_service():
    """Get Supabase service with Streamlit secrets."""
    supabase = SupabaseService(
        url=st.secrets["SUPABASE_URL"],
        key=st.secrets["SUPABASE_KEY"]
    )
    if not supabase.initialize_client():
        st.error("Failed to initialize Supabase client")
        return None
    return supabase 