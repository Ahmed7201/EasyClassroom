import streamlit as st
from datetime import datetime
from auth import authenticate
from api.classroom import ClassroomClient
from utils.bookmark_manager import BookmarkManager
from utils.theme_manager import ThemeManager
from utils.styles import load_css

st.set_page_config(page_title="Bookmarks", page_icon="⭐", layout="wide")

# Load theme
theme_manager = ThemeManager()
current_theme = theme_manager.get_theme()
load_css(current_theme)

def main():
    st.title("⭐ Bookmarked Assignments")
    
    # Initialize bookmark manager
    bookmark_mgr = BookmarkManager()
    
    # Get all bookmarks
    all_bookmarks = bookmark_mgr.get_bookmarks()
    
    if not all_bookmarks:
        st.info("📌 No bookmarks yet! Bookmark assignments from the main page to see them here.")
        return
    
    # Get all courses with bookmarks
    courses = bookmark_mgr.get_all_courses()
    
    # Course filter
    st.sidebar.subheader("🎯 Filter by Course")
    selected_course = st.sidebar.selectbox(
        "Select Course",
        ["All Courses"] + courses
    )
    
    # Filter bookmarks
    if selected_course == "All Courses":
        filtered_bookmarks = all_bookmarks
    else:
        filtered_bookmarks = bookmark_mgr.get_bookmarks(course_filter=selected_course)
    
    # Display count
    st.write(f"**{len(filtered_bookmarks)}** bookmarked assignment(s)")
    
    # Authentication (to fetch full details if needed)
    with st.spinner("Authenticating..."):
        creds = authenticate()
    
    if not creds:
        st.error("Authentication failed. Showing saved bookmark info only.")
        # Show basic info without full details
        for assignment_id, bookmark_data in filtered_bookmarks.items():
            with st.container():
                col1, col2 = st.columns([0.85, 0.15])
                
                with col1:
                    st.markdown(f"### 📚 {bookmark_data['title']}")
                    st.write(f"**Course:** {bookmark_data['course_name']}")
                    bookmarked_date = datetime.fromisoformat(bookmark_data['bookmarked_at'])
                    st.caption(f"Bookmarked on: {bookmarked_date.strftime('%B %d, %Y at %I:%M %p')}")
                
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_{assignment_id}"):
                        bookmark_mgr.remove_bookmark(assignment_id)
                        st.success("Bookmark removed!")
                        st.rerun()
                
                st.divider()
        return
    
    # Initialize Classroom client
    classroom_client = ClassroomClient(creds)
    
    # Group by course
    bookmarks_by_course = {}
    for assignment_id, bookmark_data in filtered_bookmarks.items():
        course = bookmark_data['course_name']
        if course not in bookmarks_by_course:
            bookmarks_by_course[course] = []
        bookmarks_by_course[course].append((assignment_id, bookmark_data))
    
    # Display bookmarks grouped by course
    for course_name, bookmarks in bookmarks_by_course.items():
        with st.expander(f"📖 {course_name} ({len(bookmarks)} bookmarks)", expanded=True):
            for assignment_id, bookmark_data in bookmarks:
                col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
                
                with col1:
                    st.markdown(f"#### {bookmark_data['title']}")
                    bookmarked_date = datetime.fromisoformat(bookmark_data['bookmarked_at'])
                    st.caption(f"Bookmarked: {bookmarked_date.strftime('%b %d, %Y at %I:%M %p')}")
                
                with col2:
                    # Link to Google Classroom
                    course_id = bookmark_data.get('course_id', '')
                    if course_id:
                        classroom_url = f"https://classroom.google.com/c/{course_id}/a/{assignment_id}"
                        st.link_button("🔗 Open", classroom_url)
                
                with col3:
                    if st.button("🗑️", key=f"remove_{assignment_id}", help="Remove bookmark"):
                        bookmark_mgr.remove_bookmark(assignment_id)
                        st.success("Removed!")
                        st.rerun()
                
                st.divider()

if __name__ == "__main__":
    main()
