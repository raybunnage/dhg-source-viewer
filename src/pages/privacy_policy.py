import streamlit as st
from pathlib import Path


def show_privacy_policy():
    # Read the privacy policy markdown file
    privacy_policy_path = Path(__file__).parent.parent / "docs" / "privacy-policy.md"
    with open(privacy_policy_path, "r") as f:
        privacy_policy_content = f.read()

    # Display the privacy policy
    st.markdown(privacy_policy_content)


if __name__ == "__main__":
    # st.title("Privacy Policy")
    show_privacy_policy()

# streamlit run src/pages/privacy_policy.py
