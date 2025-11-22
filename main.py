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
    page_icon="🎓",
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
    st.title("🎓 EasyClassroom")
    
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

    # Theme Colors
    is_light = st.session_state.current_theme == 'light'
    accent_color = "#2563eb" if is_light else "#bd93f9"
    btn_gradient = "linear-gradient(135deg, #2563eb 0%, #0891b2 100%)" if is_light else "linear-gradient(135deg, #bd93f9 0%, #6272a4 100%)"
    shadow_rgba = "rgba(37, 99, 235, 0.3)" if is_light else "rgba(189, 147, 249, 0.3)"
    
    # Authentication (Handled by auth.py with Cookies)
    creds = authenticate()
    
    # If authenticate returns, we are logged in
    client = ClassroomClient(creds)

    # Sidebar Profile & Settings
    with st.sidebar:
        # User Profile
        profile = client.get_user_profile()
        if profile:
            # Log user login for admin tracking
            user_email = profile.get('emailAddress', 'Unknown')
            user_name = profile.get('name', {}).get('fullName', 'Student')
            print(f"LOGIN: User {user_email} ({user_name}) accessed the app.")

            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                # Display avatar if available, else generic
                photo_url = profile.get('photoUrl', '')
                if photo_url and 'https' in photo_url:
                    # Remove size params if present to get better quality
                    if '/s' in photo_url:
                        photo_url = photo_url.split('/s')[0] + '/s100-c' # Request 100px cropped
                    
                    st.markdown(f"""
                        <div style="display: flex; justify-content: center;">
                            <img src="{photo_url}" style="border-radius: 50%; width: 60px; height: 60px; object-fit: cover; border: 2px solid {accent_color};">
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size: 40px; text-align: center;">👤</div>', unsafe_allow_html=True)
            with c2:
                st.write(f"**{profile.get('name', {}).get('fullName', 'Student')}**")
                st.caption("Ready to learn! 🚀")
        
        st.divider()
        
        st.header("⚙️ Settings")
        if st.button("🔄 Refresh Data", use_container_width=True):
            fetch_course_data.clear()
            st.rerun()

        detected_tz = get_user_timezone()
        all_timezones = pytz.all_timezones
        try:
            default_ix = all_timezones.index(detected_tz)
        except:
            default_ix = all_timezones.index('UTC')
        selected_tz = st.selectbox("🌍 Timezone", all_timezones, index=default_ix)
        
        st.divider()
        
        # Theme Toggle
        st.subheader("🎨 Theme")
        current_display = "Light Mode ☀️" if st.session_state.current_theme == 'light' else "Dark Mode 🌙"
        if st.button(f"Switch to {'Dark' if st.session_state.current_theme == 'light' else 'Light'} Mode", use_container_width=True):
            new_theme = 'dark' if st.session_state.current_theme == 'light' else 'light'
            st.session_state.current_theme = new_theme
            theme_manager.set_theme(new_theme)
            st.rerun()
        st.caption(f"Current: {current_display}")
        
        st.divider()
        st.info('"The beautiful thing about learning is that no one can take it away from you."\\n— B.B. King')
    
    # Session State for Course Selection
    if 'selected_course_id' not in st.session_state:
        st.session_state.selected_course_id = None

    # --- VIEW: COURSE LIST (HOME) ---
    if st.session_state.selected_course_id is None:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.subheader("📚 Your Courses")
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
                         deadline_str = "🔴 Overdue"
                    elif days_left == 0:
                         deadline_str = "🔴 Due Today"
                    elif days_left == 1:
                         deadline_str = "🟠 Due Tomorrow"
                    else:
                         deadline_str = f"🟢 Due in {days_left} days"
                else:
                    deadline_str = "✅ All Caught Up"

                # Create course card button - name on line 1, info on line 2
                button_label = f"📘 {course['name']}\n\n{deadline_str}  🚨 {course['pending_count']} Pending | 📂 {len(course['works'])} Items"
                
                if st.button(button_label, key=f"course_btn_{course['id']}", use_container_width=True):
                    st.session_state.selected_course_id = course['id']
                    st.session_state.selected_course_name = course['name']
                    st.rerun()

    # --- VIEW: COURSE DASHBOARD ---
    else:
        # Back Button
        if st.button("← Back to All Courses"):
            st.session_state.selected_course_id = None
            st.rerun()

        selected_course_id = st.session_state.selected_course_id
        selected_course_name = st.session_state.selected_course_name
        
        st.header(f"📌 {selected_course_name}")

        with st.spinner("Fetching assignments..."):
            works = client.get_course_work(selected_course_id)

        if not works:
            st.info("No content found! 🎉")
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
            other_works.sort(key=lambda x: x.get('creationTime', ''), reverse=True)
            
            display_works = upcoming_works + other_works

        # Initialize bookmark manager and batch operations
        bookmark_mgr = BookmarkManager()
        if 'selected_assignments' not in st.session_state:
            st.session_state.selected_assignments = []

        # --- TABS INTERFACE ---
        tab_tasks, tab_resources, tab_analytics = st.tabs(["📝 Tasks & Timeline", "📚 Resources & Files", "📊 Analytics"])

        with tab_tasks:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Quick Actions Toolbar
                st.markdown("### ⚡ Quick Actions")
                qa_col1, qa_col2, qa_col3 = st.columns(3)
                with qa_col1:
                    if st.button("📥 Sync All Files", use_container_width=True):
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
                                                f"Downloads/{selected_course_name}/{safe_title}",
                                                assignment=work,
                                                course_name=selected_course_name
                                            )
                                            if success: count += 1
                                st.success(f"Synced {count} files!")

                with qa_col2:
                    if st.button("📧 Email Teachers", use_container_width=True):
                        st.info("Go to 'Grades' tab to email specific TAs.")

                with qa_col3:
                    if st.button("📂 Open Folder", use_container_width=True):
                         import os
                         base_path = f"Downloads\\{selected_course_name}"
                         if not os.path.exists(base_path):
                             os.makedirs(base_path)
                         os.startfile(base_path)

                st.divider()
                
                # Batch Operations Toolbar
                if works and len(display_works) > 0:
                    st.markdown("### 👥 Batch Operations")
                    batch_col1, batch_col2, batch_col3 = st.columns(3)
                    
                    with batch_col1:
                        select_all = st.checkbox("✅ Select All")
                        if select_all:
                            st.session_state.selected_assignments = [w['id'] for w in display_works]
                        elif not select_all and len(st.session_state.selected_assignments) == len(display_works):
                            st.session_state.selected_assignments = []
                    
                    with batch_col2:
                        if st.button(f"📥 Download Selected ({len(st.session_state.selected_assignments)})", disabled=len(st.session_state.selected_assignments)==0):
                            files_to_download = []
                            for work in display_works:
                                if work['id'] in st.session_state.selected_assignments:
                                    for mat in work.get('materials', []):
                                        if 'driveFile' in mat:
                                            dfile = mat['driveFile']['driveFile']
                                            files_to_download.append({
                                                'file_id': dfile['id'],
                                                'file_name': dfile['title'],
                                                'mime_type': dfile.get('mimeType', ''),
                                                'destination_folder': 'Downloads',
                                                'assignment': work,
                                                'course_name': selected_course_name
                                            })
                            
                            if files_to_download:
                                progress_bar = st.progress(0)
                                def update_progress(current, total):
                                    progress_bar.progress(current / total)
                                
                                with st.spinner(f"Downloading {len(files_to_download)} files..."):
                                    results = downloader.batch_download(files_to_download, update_progress)
                                    success_count = sum(1 for r in results if r[0])
                                    st.success(f"✅ Downloaded {success_count}/{len(files_to_download)} files!")
                                    st.session_state.selected_assignments = []
                            else:
                                st.warning("No files found in selected assignments.")
                    
                    with batch_col3:
                        if st.button("🚫 Clear Selection", disabled=len(st.session_state.selected_assignments)==0):
                            st.session_state.selected_assignments = []
                            st.rerun()
                    
                    st.divider()
                
                st.subheader(f"📅 Timeline")
                
                if not works:
                     st.info("No content found! 🎉")
                
                for idx, work in enumerate(display_works):
                        # Convert to Local Time
                        local_deadline = None
                        urgency_text = ""
                        priority_color = "#6272a4" # Default Grey/Purple
                        
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
                        # Construct Metadata HTML
                        index_str = f" #{work['index']}" if work.get('index') else ""
                        meta_parts = [f"<b>Type:</b> {work['type']}{index_str}"]
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
                                if st.checkbox("☑️", key=f"select_{work['id']}_{idx}", value=is_selected, label_visibility="collapsed"):
                                    if work['id'] not in st.session_state.selected_assignments:
                                        st.session_state.selected_assignments.append(work['id'])
                                else:
                                    if work['id'] in st.session_state.selected_assignments:
                                        st.session_state.selected_assignments.remove(work['id'])
                            
                            with card_col2:
                                st.markdown(f"""
                                <div class="glass-card" style="border-left: 5px solid {priority_color}; margin-bottom: 15px; padding: 20px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <h3 style="margin:0;">{work['title']}</h3>
                                        <span style="color:{priority_color}; font-weight:bold;">{urgency_text}</span>
                                    </div>
                                    <div style="margin-top:8px; font-size:0.9em; opacity:0.8;">
                                        {meta_html}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with card_col3:
                                bookmark_icon = "⭐" if is_bookmarked else "☆"
                                if st.button(bookmark_icon, key=f"bookmark_{work['id']}_{idx}", help="Bookmark this assignment"):
                                    bookmark_mgr.toggle_bookmark(work['id'], selected_course_name, work['title'], selected_course_id)
                                    st.rerun()
                            
                            # Description
                            if work['description']:
                                with st.expander("📄 Read Description"):
                                    st.write(work['description'])
                            
                            # Materials Section
                            if work['materials']:
                                st.markdown("<div style='margin-top:10px; margin-bottom:10px; font-weight:600;'>📚 Attachments:</div>", unsafe_allow_html=True)
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
                                            st.markdown(f"<span style='font-size:0.9em;'>📄 {dfile['title']}</span>", unsafe_allow_html=True)
                                        
                                        # Download Button
                                        with c2:
                                            if is_downloaded:
                                                st.button("✅ Saved", key=f"saved_{dfile['id']}_{idx}", disabled=True)
                                            else:
                                                if st.button("⬇️ DL", key=f"dl_{dfile['id']}_{idx}"):
                                                    with st.spinner("Downloading..."):
                                                        success, path = downloader.download_file(
                                                            dfile['id'], 
                                                            dfile['title'], 
                                                            dfile.get('mimeType', ''),
                                                            f"Downloads/{selected_course_name}/{safe_title}",
                                                            assignment=work,
                                                            course_name=selected_course_name
                                                        )
                                                        if success:
                                                            st.toast(f"Saved to {path}", icon="✅")
                                                            st.rerun()
                                                        else:
                                                            st.toast("Download failed", icon="❌")

                                        # Download & Open Button
                                        with c3:
                                            if st.button("📂 Open", key=f"open_{dfile['id']}_{idx}"):
                                                with st.spinner("Opening..."):
                                                    # 1. Download if not exists
                                                    if not is_downloaded:
                                                        success, path = downloader.download_file(
                                                            dfile['id'], 
                                                            dfile['title'], 
                                                            dfile.get('mimeType', ''),
                                                            f"Downloads/{selected_course_name}/{safe_title}",
                                                            assignment=work,
                                                            course_name=selected_course_name
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
                                                            st.toast(f"Opened {dfile['title']}", icon="🚀")
                                                        else:
                                                            st.error("Could not open file.")
                                                    else:
                                                        st.error("Download failed.")

                                    elif 'link' in mat:
                                        st.markdown(f"🔗 [{mat['link']['title']}]({mat['link']['url']})")
                                    elif 'youtubeVideo' in mat:
                                        st.markdown(f"🎥 [{mat['youtubeVideo']['title']}]({mat['youtubeVideo']['alternateLink']})")

                            # Open in Classroom button
                            st.markdown(f"""
                                <div style="margin-top:10px; margin-bottom:30px;">
                                    <a href="{work['link']}" target="_blank" style="text-decoration:none;">
                                        <button style="background: {btn_gradient}; color:white; padding:10px 20px; border:none; border-radius:8px; cursor:pointer; width:100%; font-size:0.95em; font-weight:600; box-shadow: 0 2px 8px {shadow_rgba};">
                                            Open in Classroom ↗
                                        </button>
                                    </a>
                                </div>
                            """, unsafe_allow_html=True)


            with col2:
                st.subheader("📊 Quick Stats")
                st.metric("Total Items", len(works))
                st.metric("Pending", len(upcoming_works))
                
                st.divider()
                
                # Teachers & TAs
                st.subheader("👨‍🏫 Instructors")
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
                                st.markdown('<div style="font-size: 30px; text-align: center;">👤</div>', unsafe_allow_html=True)
                        
                        with t_col2:
                            st.markdown(f"**{name}**")
                            if email:
                                st.caption(f"📧 {email}")

        with tab_resources:
            st.subheader("📚 All Course Resources")
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
                        with st.expander(f"📂 {topic if topic else 'General Resources'}", expanded=True):
                            for work in topic_works:
                                st.markdown(f"**{work['title']}**")
                                for mat in work['materials']:
                                    if 'driveFile' in mat:
                                        st.markdown(f"- 📄 {mat['driveFile']['driveFile']['title']}")
                                    elif 'link' in mat:
                                        st.markdown(f"- 🔗 [{mat['link']['title']}]({mat['link']['url']})")
                                    elif 'youtubeVideo' in mat:
                                        st.markdown(f"- 🎥 [{mat['youtubeVideo']['title']}]({mat['youtubeVideo']['alternateLink']})")

        with tab_analytics:
            st.subheader("📊 Course Analytics")
            
            if not works:
                st.info("No data to analyze yet!")
            else:
                # Assignment Types Distribution
                type_counts = {}
                for w in works:
                    t = w['type']
                    type_counts[t] = type_counts.get(t, 0) + 1
                
                st.markdown("### 📋 Assignment Types")
                for atype, count in type_counts.items():
                    st.metric(atype, count)
                
                st.divider()
                
                # Deadline Status
                st.markdown("### ⏰ Deadline Status")
                overdue = sum(1 for w in works if w['deadline'] and w['deadline'] < now_utc)
                upcoming = sum(1 for w in works if w['deadline'] and w['deadline'] >= now_utc)
                no_deadline = sum(1 for w in works if not w['deadline'])
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("🔴 Overdue", overdue)
                with col_b:
                    st.metric("🟢 Upcoming", upcoming)
                with col_c:
                    st.metric("⚪ No Deadline", no_deadline)

if __name__ == "__main__":
    main()
