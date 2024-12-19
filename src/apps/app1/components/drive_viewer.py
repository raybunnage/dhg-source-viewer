import streamlit as st
from src.shared_components.service_wrapper import get_drive_service

def show_first_mp4_video():
    """Display the first MP4 video found in Google Drive."""
    drive_service = get_drive_service()
    if not drive_service:
        return

    video = drive_service.get_first_mp4()
    if video:
        st.write(f"Title: {video['name']}")
        stream_link = f"https://drive.google.com/file/d/{video['id']}/preview"
        st.markdown(
            f'<iframe src="{stream_link}" width="640" height="360"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        st.write("No mp4 files found.") 