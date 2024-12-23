def st_manage_experts():
    """
    Streamlit function to manage experts with CRUD operations
    """
    import streamlit as st
    import pandas as pd
    from datetime import datetime

    st.title("Expert Management")

    # Initialize session state for experts if it doesn't exist
    if 'experts' not in st.session_state:
        st.session_state.experts = pd.DataFrame(
            columns=['id', 'name', 'expertise', 'email', 'created_at', 'updated_at']
        )

    # Create new expert section
    st.subheader("Add New Expert")
    with st.form("add_expert_form"):
        name = st.text_input("Name")
        expertise = st.text_input("Expertise")
        email = st.text_input("Email")
        
        submit_button = st.form_submit_button("Add Expert")
        
        if submit_button and name and expertise and email:
            new_expert = {
                'id': len(st.session_state.experts) + 1,
                'name': name,
                'expertise': expertise,
                'email': email,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            st.session_state.experts = pd.concat([
                st.session_state.experts,
                pd.DataFrame([new_expert])
            ], ignore_index=True)
            st.success("Expert added successfully!")

    # Display and manage existing experts
    st.subheader("Existing Experts")
    if not st.session_state.experts.empty:
        for idx, expert in st.session_state.experts.iterrows():
            with st.expander(f"Expert: {expert['name']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**ID:** {expert['id']}")
                    st.write(f"**Name:** {expert['name']}")
                    st.write(f"**Expertise:** {expert['expertise']}")
                    st.write(f"**Email:** {expert['email']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_{expert['id']}"):
                        st.session_state.editing = expert['id']
                
                with col3:
                    if st.button("Delete", key=f"delete_{expert['id']}"):
                        st.session_state.experts = st.session_state.experts[
                            st.session_state.experts['id'] != expert['id']
                        ]
                        st.success("Expert deleted successfully!")
                        st.rerun()

                # Edit form
                if hasattr(st.session_state, 'editing') and st.session_state.editing == expert['id']:
                    with st.form(f"edit_expert_form_{expert['id']}"):
                        updated_name = st.text_input("Update Name", expert['name'])
                        updated_expertise = st.text_input("Update Expertise", expert['expertise'])
                        updated_email = st.text_input("Update Email", expert['email'])
                        
                        if st.form_submit_button("Save Changes"):
                            st.session_state.experts.loc[idx, 'name'] = updated_name
                            st.session_state.experts.loc[idx, 'expertise'] = updated_expertise
                            st.session_state.experts.loc[idx, 'email'] = updated_email
                            st.session_state.experts.loc[idx, 'updated_at'] = datetime.now()
                            del st.session_state.editing
                            st.success("Expert updated successfully!")
                            st.rerun()
    else:
        st.info("No experts found. Add your first expert using the form above.")

    # Export functionality
    if not st.session_state.experts.empty:
        st.subheader("Export Experts")
        if st.button("Export to CSV"):
            csv = st.session_state.experts.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="experts.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    st_manage_experts()


# streamlit run st_shared/st_experts.py
