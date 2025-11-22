import streamlit as st
from datetime import datetime, timedelta
import calendar as cal
import pytz
from auth import authenticate
from api.classroom import ClassroomClient
from api.calendar_api import CalendarClient
from utils.styles import load_css

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
load_css()

@st.dialog("📅 Day Events")
def show_day_events(selected_date, selected_events, calendar_client):
    """Modal dialog to show events for a specific day"""
    st.subheader(f"Events on {selected_date.strftime('%B %d, %Y')}")
    
    for evt in selected_events:
        with st.expander(f"📌 {evt['summary']}", expanded=True):
            # Time
            if evt.get('time'):
                st.write(f"**🕐 Time:** {evt['time']}")
            
            # Location/Room
            if evt.get('location'):
                st.write(f"**📍 Location:** {evt['location']}")
            
            # Description  
            if evt.get('description'):
                st.write(f"**📝 Description:**")
                st.write(evt['description'])
            else:
                st.write("*No description*")
            
            # Attendees
            if evt.get('attendees'):
                st.write(f"**👥 Attendees:** {len(evt['attendees'])} people")
            
            # Delete button
            if st.button(f"🗑️ Delete", key=f"del_dialog_{evt['id']}"):
                if calendar_client.delete_event(evt['id']):
                    st.success("Deleted!")
                    st.rerun()

def main():
    st.title("📅 Smart Calendar")
    
    # Authentication
    with st.spinner("Connecting to Google Calendar..."):
        creds = authenticate()
    
    if not creds:
        st.error("Authentication failed. Please check your credentials.json")
        return
    
    # Initialize APIs
    classroom_client = ClassroomClient(creds)
    calendar_client = CalendarClient(creds)
    
    # Tabs
    tab_view, tab_sync, tab_add, tab_manage, tab_fix = st.tabs(["📆 Calendar View", "🔄 Auto-Sync", "➕ Add Event", "🗑️ Manage Events", "🛠️ Fix Timezone"])
    
    # TAB 1: CALENDAR GRID VIEW
    with tab_view:
        # Initialize session state for current month
        if 'cal_year' not in st.session_state:
            st.session_state.cal_year = datetime.now().year
        if 'cal_month' not in st.session_state:
            st.session_state.cal_month = datetime.now().month
        
        # Month navigation
        col1, col2, col3, col4, col5 = st.columns([0.2, 0.2, 0.3, 0.2, 0.1])
        
        with col1:
            if st.button("◀ Prev"):
                if st.session_state.cal_month == 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1
                else:
                    st.session_state.cal_month -= 1
                st.rerun()
        
        with col2:
            if st.button("Today"):
                st.session_state.cal_year = datetime.now().year
                st.session_state.cal_month = datetime.now().month
                st.rerun()
        
        with col3:
            month_name = cal.month_name[st.session_state.cal_month]
            st.markdown(f"### {month_name} {st.session_state.cal_year}")
        
        with col4:
            if st.button("Next ▶"):
                if st.session_state.cal_month == 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1
                else:
                    st.session_state.cal_month += 1
                st.rerun()
        
        with col5:
            if st.button("🔄"):
                st.rerun()
        
        st.divider()
        
        # Fetch events for the month
        month_start = datetime(st.session_state.cal_year, st.session_state.cal_month, 1, tzinfo=pytz.utc)
        if st.session_state.cal_month == 12:
            month_end = datetime(st.session_state.cal_year + 1, 1, 1, tzinfo=pytz.utc)
        else:
            month_end = datetime(st.session_state.cal_year, st.session_state.cal_month + 1, 1, tzinfo=pytz.utc)
        
        # Get all events for display
        all_events = calendar_client.get_upcoming_events(max_results=100)
        
        # Filter events for this month
        month_events = []
        for event in all_events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            try:
                if 'T' in start:
                    event_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                else:
                    event_dt = datetime.fromisoformat(start).replace(tzinfo=pytz.utc)
                
                if month_start <= event_dt < month_end:
                    month_events.append({
                        'date': event_dt.date(),
                        'time': event_dt.strftime('%I:%M %p') if 'T' in start else '',
                        'summary': event.get('summary', 'No Title'),
                        'description': event.get('description', ''),
                        'location': event.get('location', ''),
                        'attendees': event.get('attendees', []),
                        'id': event.get('id')
                    })
            except:
                pass
        
        # Create calendar grid CSS
        st.markdown("""
        <style>
        .cal-header {
            font-weight: bold;
            text-align: center;
            padding: 10px;
            background: rgba(189, 147, 249, 0.2);
            border-radius: 8px;
            margin-bottom: 5px;
        }
        .cal-day {
            min-height: 100px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin: 2px;
        }
        .cal-day-num {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .cal-event {
            background: linear-gradient(135deg, #bd93f9 0%, #6272a4 100%);
            padding: 4px 8px;
            border-radius: 4px;
            margin: 3px 0;
            font-size: 0.85em;
            cursor: pointer;
            word-wrap: break-word;
        }
        .cal-today {
            background: rgba(189, 147, 249, 0.1);
            border: 2px solid #bd93f9 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                st.markdown(f'<div class="cal-header">{day}</div>', unsafe_allow_html=True)
        
        # Get calendar matrix
        month_cal = cal.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
        
        today = datetime.now().date()
        
        # Display calendar grid
        for week in month_cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown('<div class="cal-day" style="opacity:0.3;"></div>', unsafe_allow_html=True)
                    else:
                        current_date = datetime(st.session_state.cal_year, st.session_state.cal_month, day).date()
                        is_today = current_date == today
                        
                        # Get events for this day
                        day_events = [e for e in month_events if e['date'] == current_date]
                        
                        # Build day cell
                        today_class = "cal-today" if is_today else ""
                        events_html = ""
                        for evt in day_events[:3]:  # Show max 3 events per day
                            time_str = f"{evt['time']} " if evt['time'] else ""
                            summary = evt['summary'][:20] + "..." if len(evt['summary']) > 20 else evt['summary']
                            events_html += f'<div class="cal-event" title="{evt["summary"]}">{time_str}{summary}</div>'
                        
                        if len(day_events) > 3:
                            events_html += f'<div style="font-size:0.8em; opacity:0.7;">+{len(day_events)-3} more</div>'
                        
                        st.markdown(f'''
                        <div class="cal-day {today_class}" style="cursor: pointer;">
                            <div class="cal-day-num">{day}</div>
                            {events_html}
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Make entire day clickable
                        if st.button("📅", key=f"click_{current_date}_{day}", use_container_width=True):
                            if day_events:
                                show_day_events(current_date, day_events, calendar_client)
    
    # TAB 2: AUTO-SYNC
    with tab_sync:
        st.subheader("🔄 Auto-Sync Assignments")
        st.info("Automatically add upcoming assignments from your courses to Google Calendar")
        
        # Sync Configuration
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            sync_mode = st.selectbox(
                "Sync Duration",
                ["📅 Next 7 Days", "📅 Next 14 Days", "✏️ Custom Days"],
                index=0
            )
        
        with col2:
            if "Custom" in sync_mode:
                custom_days = st.number_input("Days", min_value=1, max_value=90, value=30, step=1)
            else:
                custom_days = None
        
        # Determine days
        if "7 Days" in sync_mode:
            days_ahead = 7
        elif "14 Days" in sync_mode:
            days_ahead = 14
        else:
            days_ahead = custom_days if custom_days else 30
        
        # Sync All Button
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🚀 Sync All Upcoming ({days_ahead} Days)", use_container_width=True):
                with st.spinner(f"Syncing all courses for next {days_ahead} days..."):
                    # Fetch courses only when button clicked!
                    courses = classroom_client.get_courses()
                    now = datetime.now(pytz.utc)
                    target_date = now + timedelta(days=days_ahead)
                    total_synced = 0
                    skipped = 0
                    
                    # Get existing events to avoid duplicates
                    existing_events = calendar_client.get_upcoming_events(max_results=200)
                    existing_titles = {e.get('summary', '') for e in existing_events}
                    
                    for course in courses:
                        works = classroom_client.get_course_work(course['id'])
                        # Filter: Only upcoming assignments in specified days
                        upcoming_works = [
                            w for w in works 
                            if w.get('deadline') and now < w['deadline'] <= target_date
                        ]
                        
                        for work in upcoming_works:
                            summary = f"[{work.get('type', 'ASSIGNMENT')}] {work['title']}"
                            
                            # Check for duplicates
                            if summary in existing_titles:
                                skipped += 1
                                continue
                            
                            description = work.get('description', 'No description')
                            start_time = work['deadline'] - timedelta(hours=6)  # 6 hours before
                            end_time = work['deadline']
                            
                            event_id, link = calendar_client.create_event(
                                work['title'],
                                description,
                                start_time,
                                end_time,
                                course['name'],
                                work.get('type', 'ASSIGNMENT')
                            )
                            
                            if event_id:
                                total_synced += 1
                                existing_titles.add(summary)  # Add to prevent duplicates in same sync
                    
                    if total_synced > 0:
                        st.success(f"✅ Synced {total_synced} new assignments!")
                        if skipped > 0:
                            st.info(f"⏭️ Skipped {skipped} duplicates")
                        st.balloons()
                    else:
                        st.info(f"No new assignments to sync. {skipped} already exist in your calendar.")
        
        with col2:
            if st.button("🗑️ Clean Up Past Events", use_container_width=True):
                with st.spinner("Deleting past events..."):
                    deleted = calendar_client.delete_past_events(days_ago=1)
                    st.success(f"Deleted {deleted} past event(s)!")
        
        st.divider()
        st.info("💡 Tip: Individual course sync is available. Click 'Sync All' above to sync everything at once!")
    
    # TAB 3: ADD CUSTOM EVENT
    with tab_add:
        st.subheader("➕ Add Custom Event")
        
        courses = classroom_client.get_courses()
        course_names = [c['name'] for c in courses]
        
        col1, col2 = st.columns(2)
        
        with col1:
            event_title = st.text_input("Event Title", placeholder="e.g., Study Session")
            event_type = st.selectbox("Event Type", ["LECTURE", "ASSIGNMENT", "QUIZ", "EXAM", "MIDTERM", "FINAL", "LAB", "OTHER"])
            selected_course = st.selectbox("Course", ["None"] + course_names)
        
        with col2:
            event_date = st.date_input("Date", datetime.now())
            event_time = st.time_input("Time", datetime.now().time())
            duration = st.number_input("Duration (hours)", min_value=0.5, max_value=12.0, value=1.0, step=0.5)
        
        event_description = st.text_area("Description (optional)", placeholder="Add notes or details...")
        
        if st.button("✅ Add to Calendar", use_container_width=True):
            if not event_title:
                st.error("Please enter an event title")
            else:
                # Combine date and time
                # Combine date and time
                event_datetime = datetime.combine(event_date, event_time)
                # Localize to Cairo timezone (UTC+2)
                cairo_tz = pytz.timezone('Africa/Cairo')
                event_datetime = cairo_tz.localize(event_datetime)
                # Convert to UTC for Google Calendar
                event_datetime = event_datetime.astimezone(pytz.utc)
                end_datetime = event_datetime + timedelta(hours=duration)
                
                course_name = selected_course if selected_course != "None" else ""
                
                event_id, link = calendar_client.create_event(
                    event_title,
                    event_description,
                    event_datetime,
                    end_datetime,
                    course_name,
                    event_type
                )
                
                if event_id:
                    st.success(f"✅ Event added to your calendar!")
                    st.balloons()
                    if link:
                        st.markdown(f"[Open in Google Calendar]({link})")
                else:
                    st.error("Failed to add event. Please try again.")
    
    # TAB 4: MANAGE EVENTS
    with tab_manage:
        st.subheader("🗑️ Manage Events")
        st.info("View and delete events from your calendar")
        
        events = calendar_client.get_upcoming_events(max_results=50)
        
        if not events:
            st.info("No upcoming events to manage.")
        else:
            for idx, event in enumerate(events):
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No Title')
                event_id = event['id']
                
                # Parse datetime
                try:
                    if 'T' in start:
                        event_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_str = event_dt.strftime('%b %d, %I:%M %p')
                    else:
                        time_str = start
                except:
                    time_str = start
                
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"**{summary}**")
                    st.caption(f"🕒 {time_str}")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{event_id}_{idx}"):
                        if calendar_client.delete_event(event_id):
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
                
                st.divider()
    
    # TAB 5: CALENDAR DOCTOR (Fix Timezone)
    with tab_fix:
        st.subheader("🩺 Calendar Doctor")
        st.markdown("""
        <div style="background-color: rgba(37, 99, 235, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #2563eb; margin-bottom: 20px;">
            <strong>🤖 Assistant:</strong> "I noticed that sometimes Google Calendar gets confused with timezones. 
            If you see an assignment showing up at the wrong time (like 5:00 AM instead of 11:59 PM), 
            just show me <strong>one</strong> example below, and I can fix all of them for you!"
        </div>
        """, unsafe_allow_html=True)
        
        # Step 1: Select a "Wrong" Event
        st.write("### 1. Which event looks wrong?")
        
        if st.button("🔍 Scan for My Events"):
            with st.spinner("Looking for events I added..."):
                events = calendar_client.get_upcoming_events(max_results=50)
                # Filter for app-created events
                app_events = []
                for e in events:
                    if (e.get('description') and 'Course:' in e['description']) or \
                       (e.get('summary') and '[' in e['summary'] and ']' in e['summary']):
                        app_events.append(e)
                
                if not app_events:
                    st.warning("I couldn't find any events that I added. Try syncing some assignments first!")
                else:
                    st.session_state.fix_candidates = app_events
                    st.rerun()

        if 'fix_candidates' in st.session_state and st.session_state.fix_candidates:
            # Create a selection list
            event_options = {f"{e['summary']} ({e['start'].get('dateTime', '').split('T')[0]})": e for e in st.session_state.fix_candidates}
            selected_event_name = st.selectbox("Select an event with the WRONG time:", list(event_options.keys()))
            
            if selected_event_name:
                target_event = event_options[selected_event_name]
                
                # Parse current time
                start_str = target_event['start'].get('dateTime')
                if start_str:
                    current_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    
                    st.info(f"Current Time: **{current_dt.strftime('%I:%M %p')}**")
                    
                    # Step 2: Ask for Correct Time
                    st.write("### 2. What SHOULD the time be?")
                    correct_time = st.time_input("Set the correct time:", value=current_dt.time())
                    
                    # Calculate Offset
                    # We assume the date is correct, only time is shifted
                    correct_dt = datetime.combine(current_dt.date(), correct_time)
                    correct_dt = current_dt.tzinfo.localize(correct_dt) if current_dt.tzinfo else pytz.utc.localize(correct_dt)
                    
                    # Calculate difference in hours
                    diff = (correct_dt - current_dt).total_seconds() / 3600
                    
                    if diff != 0:
                        st.write(f"⚠️ Difference: **{diff:+.1f} hours**")
                        
                        # Step 3: Offer Fix
                        st.write("### 3. How should I fix this?")
                        
                        fix_mode = st.radio("Choose an action:", 
                            ["Just fix this one event", 
                             f"Fix ALL events I added (Apply {diff:+.1f}h shift to everything)"])
                        
                        if st.button("✨ Fix It Now"):
                            with st.spinner("Applying magic fix..."):
                                success_count = 0
                                
                                if "ALL" in fix_mode:
                                    # Batch Fix
                                    progress_bar = st.progress(0)
                                    for i, evt in enumerate(st.session_state.fix_candidates):
                                        # Get current times
                                        s_str = evt['start'].get('dateTime')
                                        e_str = evt['end'].get('dateTime')
                                        
                                        if s_str and e_str:
                                            old_s = datetime.fromisoformat(s_str.replace('Z', '+00:00'))
                                            old_e = datetime.fromisoformat(e_str.replace('Z', '+00:00'))
                                            
                                            # Apply shift
                                            new_s = old_s + timedelta(hours=diff)
                                            new_e = old_e + timedelta(hours=diff)
                                            
                                            if calendar_client.update_event(evt['id'], new_s, new_e):
                                                success_count += 1
                                        
                                        progress_bar.progress((i + 1) / len(st.session_state.fix_candidates))
                                    
                                    st.success(f"🎉 I fixed {success_count} events! Your calendar should be perfect now.")
                                    
                                else:
                                    # Single Fix
                                    new_s = current_dt + timedelta(hours=diff)
                                    # Calculate duration to keep end time consistent
                                    e_str = target_event['end'].get('dateTime')
                                    old_e = datetime.fromisoformat(e_str.replace('Z', '+00:00'))
                                    duration = old_e - current_dt
                                    new_e = new_s + duration
                                    
                                    if calendar_client.update_event(target_event['id'], new_s, new_e):
                                        st.success("✅ Fixed that event for you!")
                                    else:
                                        st.error("Oops, something went wrong.")
                                
                                # Clear state to refresh
                                del st.session_state.fix_candidates
                                st.button("🔄 Refresh View")
                    else:
                        st.success("The time looks correct! No fix needed.")

if __name__ == "__main__":
    main()
