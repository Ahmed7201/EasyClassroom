import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import dateutil.parser
from auth import authenticate
from api.classroom import ClassroomClient
from utils.styles import load_css, card
from utils.time_handler import get_user_timezone, convert_to_local
from utils.downloader import DriveDownloader
from utils.theme_manager import ThemeManager
from utils.bookmark_manager import BookmarkManager

# Page Config
st.set_page_config(
    page_title="Classroom Assistant",
    page_icon="ًںژ“",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize managers
theme_manager = ThemeManager()
if 'current_theme' not in st.session_state:
    st.session_state.current_theme = theme_manager.get_theme()

# Load Premium Styles
load_css(st.session_state.current_theme)

def main():
    st.title("ًںژ“ Academic Command Center")
    
    # Authentication
    with st.spinner("Authenticating with Google..."):
        creds = authenticate()
        
    if not creds:
        st.error("Authentication failed. Please check your credentials.json")
        return

    # Initialize API
    client = ClassroomClient(creds)
    downloader = DriveDownloader(client.drive_service)
    
    # Caching Data Fetching
    @st.cache_data(ttl=3600, show_spinner="Syncing with Google Classroom...")
    def fetch_course_data(_client):
        """Fetches all course data and works. Cached for 1 hour."""
        courses = _client.get_courses()
        if not courses:
            return []
        
        data = []
        for course in courses:
            works = _client.get_course_work(course['id'])
            data.append({
                'id': course['id'],
                'name': course['name'],
                'works': works
            })
        return data

    # Sidebar Profile & Settings
    with st.sidebar:
        # User Profile
        profile = client.get_user_profile()
        if profile:
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                # Display avatar if available, else generic
                photo_url = profile.get('photoUrl', '')
                if photo_url and 'https' in photo_url:
                    # Remove size params if present to get better quality, though Classroom API usually gives a standard size
                    if '/s' in photo_url:
                        photo_url = photo_url.split('/s')[0] + '/s100-c' # Request 100px cropped
                    
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center;">
                            <img src="{photo_url}" style="border-radius: 50%; width: 60px; height: 60px; object-fit: cover; border: 2px solid #bd93f9;">
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size: 40px; text-align: center;">ًں‘¤</div>', unsafe_allow_html=True)
            with c2:
                st.write(f"**{profile.get('name', {}).get('fullName', 'Student')}**")
                st.caption("Ready to learn! ًںڑ€")
        
        st.divider()
        
        st.header("âڑ™ï¸ڈ Settings")
        if st.button("ًں”„ Refresh Data", use_container_width=True):
            fetch_course_data.clear()
            st.rerun()

        detected_tz = get_user_timezone()
        all_timezones = pytz.all_timezones
        try:
            default_ix = all_timezones.index(detected_tz)
        except:
            default_ix = all_timezones.index('UTC')
        selected_tz = st.selectbox("ًںŒچ Timezone", all_timezones, index=default_ix)
        
        st.divider()
        
        # Theme Toggle
        st.subheader("ًںژ¨ Theme")
        current_display = "Light Mode âک€ï¸ڈ" if st.session_state.current_theme == 'light' else "Dark Mode ًںŒ™"
        if st.button(f"Switch to {'Dark' if st.session_state.current_theme == 'light' else 'Light'} Mode", use_container_width=True):
            new_theme = 'dark' if st.session_state.current_theme == 'light' else 'light'
            st.session_state.current_theme = new_theme
            theme_manager.set_theme(new_theme)
            st.rerun()
        st.caption(f"Current: {current_display}")
        
        st.divider()
        st.info('"The beautiful thing about learning is that no one can take it away from you."\nâ€” B.B. King')
    
    # Session State for Course Selection
    if 'selected_course_id' not in st.session_state:
        st.session_state.selected_course_id = None

    # --- VIEW: COURSE LIST (HOME) ---
    if st.session_state.selected_course_id is None:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.subheader("ًں“ڑ Your Courses")
        with c2:
            sort_option = st.selectbox("Sort by:", ["Urgency (Next Deadline)", "Workload (Pending Tasks)", "Alphabetical (A-Z)"])

        # Fetch Data (Cached)
        raw_course_data = fetch_course_data(client)
        
        if not raw_course_data:
            st.warning("No active courses found.")
            return

        # Process Data for Display (Uncached part)
        course_data = []
        now_utc = datetime.now(pytz.utc)
        
        for course in raw_course_data:
            works = course['works']
            pending_works = [w for w in works if w['deadline'] and w['deadline'] > now_utc]
            
            next_deadline = None
            if pending_works:
                pending_works.sort(key=lambda x: x['deadline'])
                next_deadline = pending_works[0]['deadline']
            
            course_data.append({
                'id': course['id'],
                'name': course['name'],
                'works': works,
                'pending_count': len(pending_works),
                'next_deadline': next_deadline
            })
        
        # Apply Sort
        if sort_option == "Alphabetical (A-Z)":
            course_data.sort(key=lambda x: x['name'])
        elif sort_option == "Urgency (Next Deadline)":
            # Sort by next_deadline (None last)
            course_data.sort(key=lambda x: (x['next_deadline'] is None, x['next_deadline']))
        elif sort_option == "Workload (Pending Tasks)":
            course_data.sort(key=lambda x: x['pending_count'], reverse=True)

        # Display Courses in Grid
        cols = st.columns(3)
        for idx, course in enumerate(course_data):
            with cols[idx % 3]:
                # Format next deadline text
                deadline_str = ""
                if course['next_deadline']:
                    local_dl = convert_to_local(course['next_deadline'], selected_tz)
                    days_left = (course['next_deadline'] - datetime.now(pytz.utc)).days
                    if days_left < 0:
                         deadline_str = "ًں”´ Overdue"
                    elif days_left == 0:
                         deadline_str = "ًں”´ Due Today"
                    elif days_left == 1:
                         deadline_str = "ًںں  Due Tomorrow"
                    else:
                         deadline_str = f"ًںں¢ Due in {days_left} days"
                else:
                    deadline_str = "âœ… All Caught Up"

                # Create a "Card" using a large button
                label = f"ًں“ک {course['name']}\n\n{deadline_str}\nًںڑ¨ {course['pending_count']} Pending | ًں“‚ {len(course['works'])} Items"
                
                if st.button(label, key=f"course_btn_{course['id']}", use_container_width=True):
                    st.session_state.selected_course_id = course['id']
                    st.session_state.selected_course_name = course['name']
                    st.rerun()

    # --- VIEW: COURSE DASHBOARD ---
    else:
        # Back Button
        if st.button("â†گ Back to All Courses"):
            st.session_state.selected_course_id = None
            st.rerun()

        selected_course_id = st.session_state.selected_course_id
        selected_course_name = st.session_state.selected_course_name
        
        st.header(f"ًں“Œ {selected_course_name}")

        with st.spinner("Fetching assignments..."):
            # Use cached data if available, else fetch
            # For now, we re-fetch to ensure fresh materials
            works = client.get_course_work(selected_course_id)

        if not works:
            st.info("No content found! ًںژ‰")
            # Create empty lists to avoid errors if works is empty
            upcoming_works = []
            other_works = []
            display_works = []
        else:
            now_utc = datetime.now(pytz.utc)
            
            # Separate upcoming deadlines vs materials/past
            upcoming_works = []
            other_works = []
            
            for w in works:
                if w['deadline'] and w['deadline'] > now_utc:
                    upcoming_works.append(w)
                else:
                    other_works.append(w)
            
            upcoming_works.sort(key=lambda x: x['deadline'])
            # Sort others by creation time (newest first)
            other_works.sort(key=lambda x: x.get('creationTime', ''), reverse=True)
            
            # Combine: Upcoming first, then recent materials
            display_works = upcoming_works + other_works

        # Initialize bookmark manager and session state for batch operations
        bookmark_mgr = BookmarkManager()
        if 'selected_assignments' not in st.session_state:
            st.session_state.selected_assignments = []

        # --- TABS INTERFACE ---
        tab_tasks, tab_resources, tab_analytics = st.tabs(["ًں“‌ Tasks & Timeline", "ًں“ڑ Resources & Files", "ًں“ٹ Analytics"])

        with tab_tasks:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Quick Actions Toolbar
                st.markdown("### âڑ، Quick Actions")
                qa_col1, qa_col2, qa_col3 = st.columns(3)
                with qa_col1:
                    if st.button("ًں“¥ Sync All Files", use_container_width=True):
                        if not works:
                            st.warning("No files to sync.")
                        else:
                            with st.spinner("Downloading everything..."):
                                count = 0
                                for work in works:
                                    for mat in work.get('materials', []):
                                        if 'driveFile' in mat:
                                            dfile = mat['driveFile']['driveFile']
                                            safe_title = "".join([c for c in work['title'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                                            success, _ = downloader.download_file(
                                                dfile['id'], dfile['title'], dfile.get('mimeType', ''),
                                                f"Downloads/{selected_course_name}/{safe_title}"
                                            )
                                            if success: count += 1
                                st.success(f"Synced {count} files!")
                        if work['deadline']:
                            local_deadline = convert_to_local(work['deadline'], selected_tz)
                            days_left = (work['deadline'] - now_utc).days
                            
                            if days_left < 0:
                                priority_color = "#ff5555" # Dracula Red
                                urgency_text = "Overdue"
                            elif days_left == 0:
                                priority_color = "#ff5555" # Dracula Red
                                urgency_text = "Due Today!"
                            elif days_left < 3:
                                priority_color = "#ffb86c" # Dracula Orange
                                urgency_text = f"Due in {days_left} days"
                            else:
                                priority_color = "#50fa7b" # Dracula Green
                                urgency_text = f"Due in {days_left} days"
                        else:
                            # Material or No Deadline
                            if work['type'] == 'MATERIAL':
                                priority_color = "#8be9fd" # Cyan for Materials
                                urgency_text = "Resource"
                            else:
                                urgency_text = "No Deadline"

                        # Construct Metadata HTML
                        meta_parts = [f"<b>Type:</b> {work['type']}{f' #{work['index']}' if work['index'] else ''}"]
                        if work['topic']:
                            meta_parts.append(f"<b>Topic:</b> {work['topic']}")
                        if local_deadline:
                            meta_parts.append(f"<b>Due:</b> {local_deadline.strftime('%b %d, %I:%M %p')}")
                        
                        # Add Points and Posted Date
                        if work.get('max_points'):
                            meta_parts.append(f"<b>Pts:</b> {work['max_points']}")
                        
                        # Creation Time
                        if work.get('creationTime'):
                            try:
                                created_dt = dateutil.parser.isoparse(work['creationTime'])
                                meta_parts.append(f"<span style='font-size:0.8em; opacity:0.6'>Posted {created_dt.strftime('%b %d')}</span>")
                            except: pass

                        meta_html = " <span style='opacity:0.5'>|</span> ".join(meta_parts)

                        # Card UI with Checkbox and Bookmark
                        with st.container():
                            # Check Status
                            is_selected = work['id'] in st.session_state.selected_assignments
                            is_bookmarked = bookmark_mgr.is_bookmarked(work['id'])
                            
                            # Checkbox and Bookmark row
                            card_col1, card_col2, card_col3 = st.columns([0.05, 0.85, 0.1])
                            with card_col1:
                                if st.checkbox("âک‘ï¸ڈ", key=f"select_{work['id']}_{idx}", value=is_selected, label_visibility="collapsed"):
                                    if work['id'] not in st.session_state.selected_assignments:
                                        st.session_state.selected_assignments.append(work['id'])
                                else:
                                    if work['id'] in st.session_state.selected_assignments:
                                        st.session_state.selected_assignments.remove(work['id'])
                            
                            with card_col2:
                                st.markdown(f"""
                                <div class="glass-card" style="border-left: 5px solid {priority_color}; margin-bottom: 15px; padding: 20px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <h3 style="margin:0; color:#f8f8f2 !important;">{work['title']}</h3>
                                        <span style="color:{priority_color}; font-weight:bold;">{urgency_text}</span>
                                    </div>
                                    <div style="margin-top:8px; font-size:0.9em; opacity:0.8;">
                                        {meta_html}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with card_col3:
                                bookmark_icon = "â­گ" if is_bookmarked else "âک†"
                                if st.button(bookmark_icon, key=f"bookmark_{work['id']}_{idx}", help="Bookmark this assignment"):
                                    bookmark_mgr.toggle_bookmark(work['id'], selected_course_name, work['title'], selected_course_id)
                                    st.rerun()
                            
                            # Description
                            if work['description']:
                                with st.expander("ًں“„ Read Description"):
                                    st.write(work['description'])
                            
                            # Materials Section
                            if work['materials']:
                                st.markdown("<div style='margin-top:10px; margin-bottom:10px; font-weight:600;'>ًں“ڑ Attachments:</div>", unsafe_allow_html=True)
                                for mat in work['materials']:
                                    if 'driveFile' in mat:
                                        dfile = mat['driveFile']['driveFile']
                                        
                                        # Check if file exists locally
                                        import os
                                        safe_title = "".join([c for c in work['title'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                                        file_path = f"Downloads/{selected_course_name}/{safe_title}/{dfile['title']}"
                                        is_downloaded = os.path.exists(file_path)

                                        c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                                        
                                        with c1:
                                            st.markdown(f"<span style='font-size:0.9em;'>ًں“„ {dfile['title']}</span>", unsafe_allow_html=True)
                                        
                                        # Download Button
                                        with c2:
                                            if is_downloaded:
                                                st.button("âœ… Saved", key=f"saved_{dfile['id']}_{idx}", disabled=True)
                                            else:
                                                if st.button("â¬‡ï¸ڈ DL", key=f"dl_{dfile['id']}_{idx}"):
                                                    with st.spinner("Downloading..."):
                                                        success, path = downloader.download_file(
                                                            dfile['id'], 
                                                            dfile['title'], 
                                                            dfile.get('mimeType', ''),
                                                            f"Downloads/{selected_course_name}/{safe_title}"
                                                        )
                                                        if success:
                                                            st.toast(f"Saved to {path}", icon="âœ…")
                                                            st.rerun()
                                                        else:
                                                            st.toast("Download failed", icon="â‌Œ")

                                        # Download & Open Button
                                        with c3:
                                            if st.button("ًں“‚ Open", key=f"open_{dfile['id']}_{idx}"):
                                                with st.spinner("Opening..."):
                                                    # 1. Download if not exists
                                                    if not is_downloaded:
                                                        success, path = downloader.download_file(
                                                            dfile['id'], 
                                                            dfile['title'], 
                                                            dfile.get('mimeType', ''),
                                                            f"Downloads/{selected_course_name}/{safe_title}"
                                                        )
                                                    else:
                                                        success = True
                                                        path = file_path

                                                    # 2. Open
                                                    if success:
                                                        # Ensure path is absolute for os.startfile
                                                        abs_path = os.path.abspath(path)
                                                        opened = downloader.open_file(abs_path)
                                                        if opened:
                                                            st.toast(f"Opened {dfile['title']}", icon="ًںڑ€")
                                                        else:
                                                            st.error("Could not open file.")
                                                    else:
                                                        st.error("Download failed.")

                                    elif 'link' in mat:
                                        st.markdown(f"ًں”— [{mat['link']['title']}]({mat['link']['url']})")
                                    elif 'youtubeVideo' in mat:
                                        st.markdown(f"ًںژ¥ [{mat['youtubeVideo']['title']}]({mat['youtubeVideo']['alternateLink']})")

                            # Open in Classroom button - outside the card for better spacing
                            st.markdown(f"""
                                <div style="margin-top:10px; margin-bottom:30px;">
                                    <a href="{work['link']}" target="_blank" style="text-decoration:none;">
                                        <button style="background: linear-gradient(135deg, #bd93f9 0%, #6272a4 100%); color:white; padding:10px 20px; border:none; border-radius:8px; cursor:pointer; width:100%; font-size:0.95em; font-weight:600; box-shadow: 0 2px 8px rgba(189, 147, 249, 0.3);">
                                            Open in Classroom â†—
                                        </button>
                                    </a>
                                </div>
                            """, unsafe_allow_html=True)


            with col2:
                st.subheader("ًں“ٹ Quick Stats")
                st.metric("Total Items", len(works))
                st.metric("Pending", len(upcoming_works))
                
                st.divider()
                
                # Teachers & TAs
                st.subheader("ًں‘¨â€چًںڈ« Instructors")
                teachers = client.get_teachers(selected_course_id, selected_course_name)
                if teachers:
                    for teacher in teachers:
                        profile = teacher.get('profile', {})
                        name = profile.get('name', {}).get('fullName', 'Unknown')
                        email = profile.get('emailAddress', '')
                        photo_url = profile.get('photoUrl', '')
                        
                        t_col1, t_col2 = st.columns([0.15, 0.85])
                        with t_col1:
                            if photo_url:
                                if not photo_url.startswith('http'):
                                    photo_url = f"https:{photo_url}"
                                if '/s' in photo_url:
                                    photo_url = photo_url.split('/s')[0] + '/s100-c'
                                st.markdown(f'<img src="{photo_url}" style="border-radius: 50%; width: 50px; height: 50px; object-fit: cover;">', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="font-size: 30px; text-align: center;">ًں‘¤</div>', unsafe_allow_html=True)
                        
                        with t_col2:
                            st.markdown(f"**{name}**")
                            if email:
                                st.caption(f"ًں“§ {email}")
                                # Use HTML mailto link that opens in Gmail
                                gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={email}"
                                st.markdown(f"""<a href="{gmail_url}" target="_blank">
                                    <button style="background: linear-gradient(135deg, #bd93f9 0%, #6272a4 100%); color:white; padding:6px 12px; border:none; border-radius:6px; cursor:pointer; width:100%; margin-top:5px;">
                                        âœ‰ï¸ڈ Send Email
                                    </button>
                                </a>""", unsafe_allow_html=True)
                        st.divider()
                else:
                    st.info("No instructors found.")
                
                st.divider()
                
                # Grade Calculator
                st.subheader("ًں§® Grade Target")
                current = st.number_input("Current Grade (%)", 0, 100, 85)
                target = st.number_input("Target Grade (%)", 0, 100, 90)
                final_weight = st.slider("Final Exam Weight", 0, 100, 40)
                
                if final_weight > 0:
                    needed = (target - (current * (1 - final_weight/100))) / (final_weight/100)
                    if needed > 100:
                        st.error(f"You need {needed:.1f}% (Impossible ًںک¢)")
                    elif needed < 0:
                        st.success(f"You need {needed:.1f}% (Already passed! ًںژ‰)")
                    else:
                        st.warning(f"You need **{needed:.1f}%** on the final.")

        # --- TAB: RESOURCES ---
        with tab_resources:
            st.subheader("ًں“ڑ Course Materials Library")
            # Filter for items with materials
            material_items = [w for w in works if w.get('materials')]
            
            if not material_items:
                st.info("No materials found.")
            else:
                # Group by Topic
                topics = sorted(list(set([w['topic'] for w in material_items if w['topic']])))
                if 'UNCATEGORIZED' not in topics: topics.append('UNCATEGORIZED')
                
                for topic in topics:
                    topic_works = [w for w in material_items if w['topic'] == topic or (topic == 'UNCATEGORIZED' and not w['topic'])]
                    if topic_works:
                        with st.expander(f"ًں“‚ {topic if topic else 'General Resources'}", expanded=True):
                            for work in topic_works:
                                st.markdown(f"**{work['title']}**")
                                for mat in work['materials']:
                                    if 'driveFile' in mat:
                                        st.markdown(f"- ًں“„ {mat['driveFile']['driveFile']['title']}")
                                    elif 'link' in mat:
                                        st.markdown(f"- ًں”— [{mat['link']['title']}]({mat['link']['url']})")
                                    elif 'youtubeVideo' in mat:
                                        st.markdown(f"- ًںژ¥ [{mat['youtubeVideo']['title']}]({mat['youtubeVideo']['alternateLink']})")
                                st.divider()

        # --- TAB: ANALYTICS ---
        with tab_analytics:
            st.subheader("ًں“ٹ Course Analytics")
            
            # 1. Assignment Distribution
            type_counts = {}
            for w in works:
                t = w['type']
                type_counts[t] = type_counts.get(t, 0) + 1
            
            ac1, ac2 = st.columns(2)
            with ac1:
                st.write("**Workload Distribution**")
                st.bar_chart(type_counts)
            
            with ac2:
                st.write("**Upcoming Deadlines**")
                if upcoming_works:
                    # Create a simple dataframe for the chart
                    df_deadlines = pd.DataFrame([
                        {'Task': w['title'], 'Date': w['deadline']} for w in upcoming_works
                    ])
                    st.dataframe(df_deadlines, hide_index=True)
                else:
                    st.success("No upcoming deadlines!")

if __name__ == "__main__":
    main()
