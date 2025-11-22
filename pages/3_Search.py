import streamlit as st
from auth import authenticate
from api.classroom import ClassroomClient
from utils.styles import load_css, card

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
load_css()

def main():
    st.title("🔍 Global Search")
    
    creds = authenticate()
    if not creds:
        st.error("Please log in first.")
        return

    client = ClassroomClient(creds)
    
    query = st.text_input("Search for assignments, quizzes, or materials...", placeholder="e.g., 'Calculus Midterm' or 'Physics PDF'")
    
    if query:
        with st.spinner("Searching across all courses..."):
            courses = client.get_courses()
            results = []
            
            for course in courses:
                works = client.get_course_work(course['id'])
                for work in works:
                    # Search in Title and Description
                    if query.lower() in work['title'].lower() or \
                       (work['description'] and query.lower() in work['description'].lower()):
                        results.append({
                            'course': course['name'],
                            'work': work
                        })
            
            if not results:
                st.warning("No matches found.")
            else:
                st.success(f"Found {len(results)} matches!")
                for res in results:
                    work = res['work']
                    content = f"""
                    <p>{work['description'][:150]}...</p>
                    <a href="{work['link']}" target="_blank" style="text-decoration:none; color:#8be9fd;">Open in Classroom ↗</a>
                    """
                    card(work['title'], content, footer=f"Course: {res['course']}")

if __name__ == "__main__":
    main()
