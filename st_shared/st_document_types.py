import streamlit as st
from pathlib import Path
import sys
import pandas as pd

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
from src.services.supabase_service import SupabaseService
from src.db.uni_document_types import DocumentTypes


@st.cache_resource
def get_document_types_service():
    """Initialize SupabaseService and DocumentTypes as a cached resource"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = SupabaseService(url, key)
    email = st.secrets["TEST_EMAIL"]
    password = st.secrets["TEST_PASSWORD"]
    supabase.login(email, password)
    return DocumentTypes(supabase)


def st_manage_document_types(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(layout="wide")

    # Get cached document types service
    document_types = get_document_types_service()

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.sidebar.title("Manage Document Types")
        st.sidebar.subheader("Actions")
        action = st.sidebar.radio("Select Action", ["Add", "Edit", "Delete", "Alias"])

        if action == "Add":
            st.subheader("Add Document Type")
            document_type_name = st.text_input("Document Type Name")
            description = st.text_input("Description")
            mime_type = st.text_input("Mime Type")
            file_extension = st.text_input("File Extension")
            category = st.text_input("Category")
            is_ai_generated = st.checkbox("Is AI Generated", value=False)
            if st.button("Add Document Type"):
                result = document_types.add(
                    document_type_name,
                    description,
                    mime_type,
                    file_extension,
                    category,
                    is_ai_generated,
                )
                if result:
                    st.success(
                        f"Document Type '{document_type_name}' added successfully"
                    )
                else:
                    st.error(f"Failed to add document type for {document_type_name}")

        elif action == "Edit":
            st.subheader("Edit Document Type")
            document_types_list = document_types.get_all()
            if not document_types_list:
                st.warning("No document types found in the database")
                return

            document_type_options = sorted(
                [
                    (
                        document_type["id"],
                        document_type["document_type"],
                        document_type.get("description", ""),
                        document_type.get("mime_type", ""),
                        document_type.get("file_extension", ""),
                        document_type.get("category", ""),
                        document_type.get("is_ai_generated", False),
                    )
                    for document_type in document_types_list
                ],
                key=lambda x: x[1],
            )
            selected_document_type = st.selectbox(
                "Select Document Type to Edit",
                document_type_options,
                format_func=lambda x: x[1],
                key="select_document_type_to_edit",
            )
            if selected_document_type:
                selected_document_type_id = selected_document_type[0]
                selected_document_type_name = selected_document_type[1]
                selected_document_type_description = selected_document_type[2]
                selected_document_type_mime_type = selected_document_type[3]
                selected_document_type_file_extension = selected_document_type[4]
                selected_document_type_category = selected_document_type[5]
                selected_document_type_is_ai_generated = selected_document_type[6]
                document_type_name = st.text_input(
                    "Document Type Name", value=selected_document_type_name
                )
                description = st.text_input(
                    "Description", value=selected_document_type_description
                )
                mime_type = st.text_input(
                    "Mime Type", value=selected_document_type_mime_type
                )
                file_extension = st.text_input(
                    "File Extension", value=selected_document_type_file_extension
                )
                category = st.text_input(
                    "Category", value=selected_document_type_category
                )
                is_ai_generated = st.checkbox(
                    "Is AI Generated", value=selected_document_type_is_ai_generated
                )
                if st.button("Update Document Type"):
                    update_document_type = {
                        "document_type_name": document_type_name,
                        "description": description,
                        "mime_type": mime_type,
                        "file_extension": file_extension,
                        "category": category,
                        "is_ai_generated": is_ai_generated,
                    }
                    document_type = document_types.update(
                        selected_document_type_id, update_document_type
                    )
                    if document_type:
                        st.success(
                            f"Document Type updated successfully for {selected_document_type_name}"
                        )
                    else:
                        st.error(
                            f"Failed to update document type for {selected_document_type_name}"
                        )

        elif action == "Delete":
            st.subheader("Delete Document Type")
            document_types_delete = document_types.get_all()
            document_type_deletes = sorted(
                [
                    (document_type["id"], document_type["document_type"])
                    for document_type in document_types_delete
                ],
                key=lambda x: x[1],
            )
            selected_document_type_id, selected_document_type_name = st.selectbox(
                "Select Document Type to Delete",
                document_type_deletes,
                format_func=lambda x: x[1],
                key="select_document_type_to_delete",
            )
            if selected_document_type_name:
                if st.button("Delete Document Type"):
                    result = document_types.delete(selected_document_type_id)
                    if result is True:
                        st.success(
                            f"Document Type '{selected_document_type_name}' deleted successfully"
                        )
                        st.rerun()  # Updated from st.experimental_rerun()
                    else:
                        st.error(
                            f"Failed to delete document type '{selected_document_type_name}'"
                        )

        elif action == "Alias":
            st.subheader("Alias Document Type")
            alias_name = st.text_input("Alias Name")
            document_types_alias = document_types.get_all()
            document_type_aliases = sorted(
                [
                    (document_type["id"], document_type["document_type"])
                    for document_type in document_types_alias
                ],
                key=lambda x: x[1],
            )
            selected_document_type_id, selected_document_type_name = st.selectbox(
                "Select Document Type to Delete",
                document_type_aliases,
                format_func=lambda x: x[1],
                key="select_document_type_to_alias",
            )
            if selected_document_type_name:
                if st.button("Add Alias"):
                    result = document_types.add_alias(
                        selected_document_type_name, alias_name
                    )
                    if result:
                        st.success(f"Alias '{alias_name}' added successfully")
                    else:
                        st.error(f"Failed to add alias '{alias_name}'")

            aliases = document_types.get_aliases_by_document_type_name(
                selected_document_type_name
            )
            if aliases:
                st.subheader(f"Aliases for {selected_document_type_name}")
                # Convert aliases to a pandas DataFrame and display available columns
                df = pd.DataFrame(aliases)
                df = df[
                    ["id", "alias_name"]
                ]  # Select only id and document_type_alias columns
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config={
                        "alias_name": st.column_config.Column(width=300)
                    },
                )

                alias_id_to_delete = st.number_input(
                    "Enter Alias ID to Delete", min_value=0, step=1
                )
                if alias_id_to_delete:
                    if st.button("Delete Alias"):
                        result = document_types.delete_alias(alias_id_to_delete)
                        if result:
                            st.success(
                                f"Alias with ID '{alias_id_to_delete}' deleted successfully"
                            )
                            st.rerun()  # Refresh the page after deleting alias
                        else:
                            st.error(
                                f"Failed to delete alias with ID '{alias_id_to_delete}'"
                            )
            else:
                st.warning(f"No aliases found for {selected_document_type_name}")

    with col2:
        st.subheader("All Document Types")
        document_types_list = document_types.get_all()
        if document_types_list:
            # Remove 'id' and 'user_id' from each document type dictionary
            for document_type in document_types_list:
                document_type.pop("id", None)
            st.dataframe(document_types_list, width=1000, height=600)
        else:
            st.warning("No document types found in the database")


# 7c119aee-33f1-438a-b81f-f3d4bb066e8b
if __name__ == "__main__":
    st_manage_document_types()

# streamlit run st_shared/st_document_types.py
