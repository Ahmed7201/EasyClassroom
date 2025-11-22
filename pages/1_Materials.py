import streamlit as st
import os
from auth import authenticate
from api.classroom import ClassroomClient
from api.gmail import GmailClient
from utils.downloader import DriveDownloader
from utils.styles import load_css

st.set_page_config(page_title="Materials", page_icon="📚", layout="wide")
load_css()

def main():
    st.title("📚 Course Materials")
    
    creds = authenticate()
    if not creds:
        st.error("Please log in first.")
        return

    client = ClassroomClient(creds)
    gmail_client = GmailClient(creds)
    downloader = DriveDownloader(client.drive_service)

    # Sidebar
    courses = client.get_courses()
    if not courses:
        st.warning("No courses found.")
        return
        
    selected_course_name = st.sidebar.selectbox("Select Course", [c['name'] for c in courses])
    selected_course = next(c for c in courses if c['name'] == selected_course_name)

    # Ask TA Button in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🙋‍♂️ Need Help?")
    if st.sidebar.button("Ask TA / Professor"):
        teachers = client.get_teachers(selected_course['id'], selected_course['name'])
        st.sidebar.write("Select recipient:")
        for teacher in teachers:
            name = teacher.get('profile', {}).get('name', {}).get('fullName', 'Unknown')
            email = teacher.get('profile', {}).get('emailAddress')
            photo_url = teacher.get('profile', {}).get('photoUrl', '')
            
            t_col1, t_col2 = st.sidebar.columns([0.25, 0.75])
            with t_col1:
                if photo_url:
                    if not photo_url.startswith('http'):
                        photo_url = f"https:{photo_url}"
                    if '/s' in photo_url:
                        photo_url = photo_url.split('/s')[0] + '/s100-c'
                    st.markdown(f'<img src="{photo_url}" style="border-radius: 50%; width: 40px; height: 40px; object-fit: cover;">', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size: 24px; text-align: center;">👤</div>', unsafe_allow_html=True)
            
            with t_col2:
                if st.button(f"📧 {name}", key=f"side_email_{email}"):
                    draft = gmail_client.create_draft(
                        email, 
                        f"Question regarding {selected_course_name}", 
                        f"Dear {name},\n\nI have a question about {selected_course_name}.\n\n[Your question here]\n\nBest,"
                    )
                    if draft:
                        st.sidebar.success("Draft created!")
                    else:
                        st.sidebar.error("Error creating draft.")

    # Fetch Materials
    with st.spinner(f"Fetching materials for {selected_course_name}..."):
        # Note: In a real app, we'd have a dedicated get_course_materials method
        # reusing get_course_work for now as it contains materials too
        works = client.get_course_work(selected_course['id'])

    for work in works:
        if not work['materials']:
            continue

        with st.expander(f"{work['title']} ({len(work['materials'])} files)"):
            for mat in work['materials']:
                # Handle Drive Files
                if 'driveFile' in mat:
                    dfile = mat['driveFile']['driveFile']
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 {dfile['title']}")
                    with col2:
                        if st.button("Download", key=dfile['id']):
                            with st.spinner("Downloading..."):
                                success, path = downloader.download_file(
                                    dfile['id'], 
                                    dfile['title'], 
                                    dfile.get('mimeType', ''),
                                    f"Downloads/{selected_course_name}/{work['title']}"
                                )
                                if success:
                                    st.success(f"Saved to {path}")
                                else:
                                    st.error(f"Failed: {path}")
                
                # Handle Links
                elif 'link' in mat:
                    st.markdown(f"🔗 [{mat['link']['title']}]({mat['link']['url']})")
                
                # Handle YouTube
                elif 'youtubeVideo' in mat:
                    st.markdown(f"🎥 [{mat['youtubeVideo']['title']}]({mat['youtubeVideo']['alternateLink']})")

if __name__ == "__main__":
    main()
