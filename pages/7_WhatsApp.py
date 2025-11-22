import streamlit as st
from datetime import datetime
import pytz
import json
import os
from auth import authenticate
from api.classroom import ClassroomClient
from utils.whatsapp_notifier import WhatsAppNotifier
from utils.styles import load_css

st.set_page_config(page_title="WhatsApp Notifications", page_icon="📱", layout="wide")
load_css()

SETTINGS_FILE = "whatsapp_settings.json"

def load_settings():
    """Load WhatsApp settings from file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        "phone_number": "+201127063811",
        "api_key": "",
        "daily_summary_enabled": True,
        "new_assignment_alerts": True,
        "summary_time": "08:00",
        "timezone": "Africa/Cairo"
    }

def save_settings(settings):
    """Save WhatsApp settings to file"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def main():
    st.title("📱 WhatsApp Notifications")
    
    # Authentication
    with st.spinner("Authenticating..."):
        creds = authenticate()
    
    if not creds:
        st.error("Authentication failed. Please check your credentials.json")
        return
    
    # Initialize API
    classroom_client = ClassroomClient(creds)
    
    # Load settings
    settings = load_settings()
    
    # Tabs
    tab_setup, tab_test, tab_manual = st.tabs(["⚙️ Setup", "🧪 Test", "📤 Send Manual Message"])
    
    # TAB 1: SETUP
    with tab_setup:
        st.subheader("⚙️ WhatsApp Notification Setup")
        
        st.info("""
        **📌 Setup Instructions:**
        1. Save this number in your contacts: **+34 644 44 32 09**
        2. Send this message to that number on WhatsApp: **I allow callmebot to send me messages**
        3. You'll receive your **API Key** in response
        4. Enter your API Key below
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            phone_number = st.text_input(
                "📱 Your WhatsApp Number",
                value=settings.get("phone_number", "+201127063811"),
                help="Include country code (e.g., +201127063811)"
            )
            
            api_key = st.text_input(
                "🔑 CallMeBot API Key",
                value=settings.get("api_key", ""),
                type="password",
                help="Get this from CallMeBot after registration"
            )
        
        with col2:
            timezone = st.selectbox(
                "🌍 Timezone",
                ["Africa/Cairo", "UTC", "US/Eastern", "US/Pacific", "Europe/London", "Asia/Dubai"],
                index=0 if settings.get("timezone", "Africa/Cairo") == "Africa/Cairo" else 0,
                help="Your local timezone for message timestamps"
            )
            
            daily_summary = st.checkbox(
                "📅 Daily Summary",
                value=settings.get("daily_summary_enabled", True),
                help="Send a summary of all assignments every morning"
            )
            
            # Parse existing time or use default
            existing_time = settings.get("summary_time", "08:00")
            try:
                hour_24 = int(existing_time.split(":")[0])
                minute = int(existing_time.split(":")[1])
                hour_12 = hour_24 if hour_24 <= 12 else hour_24 - 12
                if hour_12 == 0:
                    hour_12 = 12
                am_pm = "AM" if hour_24 < 12 else "PM"
            except:
                hour_12 = 8
                minute = 0
                am_pm = "AM"
            
            st.write("🕐 Summary Time")
            time_col1, time_col2, time_col3 = st.columns([1, 1, 1])
            with time_col1:
                summary_hour = st.selectbox("Hour", list(range(1, 13)), index=hour_12-1, key="hour")
            with time_col2:
                summary_minute = st.selectbox("Minute", [0, 15, 30, 45], index=[0, 15, 30, 45].index(minute) if minute in [0, 15, 30, 45] else 0, key="minute")
            with time_col3:
                summary_ampm = st.selectbox("AM/PM", ["AM", "PM"], index=0 if am_pm == "AM" else 1, key="ampm")
            
            # Convert to 24-hour format for storage
            hour_24_final = summary_hour if summary_ampm == "AM" else summary_hour + 12
            if summary_hour == 12 and summary_ampm == "AM":
                hour_24_final = 0
            elif summary_hour == 12 and summary_ampm == "PM":
                hour_24_final = 12
            
            # Show preview of when message will be sent
            tz = pytz.timezone(timezone)
            now_local = datetime.now(tz)
            next_send = now_local.replace(hour=hour_24_final, minute=summary_minute, second=0, microsecond=0)
            if next_send < now_local:
                from datetime import timedelta
                next_send = next_send + timedelta(days=1)
            
            st.info(f"📅 Next summary will be sent at: **{next_send.strftime('%B %d, %Y - %I:%M %p')}** ({timezone})")
            
            new_alerts = st.checkbox(
                "🔔 New Assignment Alerts",
                value=settings.get("new_assignment_alerts", True),
                help="Get notified when new assignments are posted"
            )
        
        st.divider()
        
        if st.button("💾 Save Settings", use_container_width=True):
            new_settings = {
                "phone_number": phone_number,
                "api_key": api_key,
                "daily_summary_enabled": daily_summary,
                "new_assignment_alerts": new_alerts,
                "summary_time": f"{hour_24_final:02d}:{summary_minute:02d}",
                "timezone": timezone
            }
            save_settings(new_settings)
            st.success("✅ Settings saved successfully!")
            st.balloons()
    
    # TAB 2: TEST
    with tab_test:
        st.subheader("🧪 Test Connection")
        
        if not settings.get("api_key"):
            st.warning("⚠️ Please set up your API Key in the Setup tab first!")
        else:
            st.info(f"📱 Send test message to: **{settings['phone_number']}**")
            
            if st.button("📨 Send Test Message", use_container_width=True):
                with st.spinner("Sending..."):
                    notifier = WhatsAppNotifier(settings['phone_number'], settings['api_key'], settings.get('timezone', 'Africa/Cairo'))
                    success, message = notifier.test_connection()
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.success("Check your WhatsApp! 📱")
                    else:
                        st.error(f"❌ {message}")
                        st.info("💡 Make sure you've registered with CallMeBot first!")
    
    # TAB 3: MANUAL MESSAGE
    with tab_manual:
        st.subheader("📤 Send Manual Summary")
        
        if not settings.get("api_key"):
            st.warning("⚠️ Please set up your API Key in the Setup tab first!")
        else:
            action = st.radio(
                "Choose action:",
                ["📚 Send Daily Summary", "🚨 Send Alert for New Assignments"]
            )
            
            if st.button("📨 Send Now", use_container_width=True):
                with st.spinner("Fetching assignments and sending..."):
                    notifier = WhatsAppNotifier(settings['phone_number'], settings['api_key'], settings.get('timezone', 'Africa/Cairo'))
                    
                    if "Daily Summary" in action:
                        # Get all assignments from all courses
                        courses = classroom_client.get_courses()
                        all_assignments = []
                        
                        for course in courses:
                            works = classroom_client.get_course_work(course['id'])
                            for work in works:
                                work['course_name'] = course['name']
                                all_assignments.append(work)
                        
                        # Format and send
                        message = notifier.format_daily_summary(all_assignments)
                        success, result = notifier.send_message(message)
                        
                        if success:
                            st.success("✅ Daily summary sent!")
                            st.code(message)
                        else:
                            st.error(f"❌ {result}")
                    
                    else:
                        # Get recent assignments (last 3 days)
                        courses = classroom_client.get_courses()
                        recent_assignments = []
                        now = datetime.now(pytz.utc)
                        
                        for course in courses:
                            works = classroom_client.get_course_work(course['id'])
                            for work in works:
                                # Check if created in last 3 days
                                if work.get('creationTime'):
                                    import dateutil.parser
                                    created = dateutil.parser.isoparse(work['creationTime'])
                                    if (now - created).days <= 3:
                                        work['course_name'] = course['name']
                                        recent_assignments.append(work)
                        
                        if not recent_assignments:
                            st.info("No new assignments in the last 3 days!")
                        else:
                            sent_count = 0
                            for assignment in recent_assignments:
                                message = notifier.format_new_assignment_alert(assignment)
                                success, result = notifier.send_message(message)
                                if success:
                                    sent_count += 1
                            
                            st.success(f"✅ Sent {sent_count} alerts!")

if __name__ == "__main__":
    main()
