import streamlit as st
import os
from auth import authenticate
from api.classroom import ClassroomClient
from utils.styles import load_css, card

st.set_page_config(page_title="Notes", page_icon="📝", layout="wide")
load_css()

def main():
    st.title("📝 Course Notes")
    
    creds = authenticate()
    if not creds:
        st.error("Please log in first.")
        return

    client = ClassroomClient(creds)
    courses = client.get_courses()
    
    if not courses:
        st.warning("No courses found.")
        return

    # Sidebar
    selected_course_name = st.sidebar.selectbox("Select Course", [c['name'] for c in courses])
    
    # Notes Directory
    notes_dir = f"Notes/{selected_course_name}"
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
        
    # List existing notes
    files = [f for f in os.listdir(notes_dir) if f.endswith(".txt")]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Your Notes")
        selected_file = st.radio("Select a note", ["+ New Note"] + files)
        
    with col2:
        if selected_file == "+ New Note":
            st.subheader("Create New Note")
            new_title = st.text_input("Title")
            new_content = st.text_area("Content", height=300)
            if st.button("Save Note"):
                if new_title:
                    with open(f"{notes_dir}/{new_title}.txt", "w") as f:
                        f.write(new_content)
                    st.success("Note saved!")
                    st.rerun()
                else:
                    st.error("Please enter a title.")
        else:
            st.subheader(f"Editing: {selected_file}")
            with open(f"{notes_dir}/{selected_file}", "r") as f:
                content = f.read()
            
            updated_content = st.text_area("Content", value=content, height=300)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Update Note"):
                    with open(f"{notes_dir}/{selected_file}", "w") as f:
                        f.write(updated_content)
                    st.success("Updated!")
            with c2:
                if st.button("🗑 Delete", type="primary"):
                    os.remove(f"{notes_dir}/{selected_file}")
                    st.rerun()

if __name__ == "__main__":
    main()
