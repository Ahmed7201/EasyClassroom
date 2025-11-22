import requests
import pytz
from datetime import datetime
import streamlit as st

def get_user_timezone():
    """
    Detects user timezone based on IP or returns default.
    """
    if 'user_timezone' not in st.session_state:
        try:
            # Free API to get timezone from IP
            response = requests.get('http://ip-api.com/json/')
            data = response.json()
            st.session_state.user_timezone = data.get('timezone', 'UTC')
        except:
            st.session_state.user_timezone = 'UTC'
    
    return st.session_state.user_timezone

def convert_to_local(utc_dt, target_tz_str):
    """
    Converts a UTC datetime object to the target timezone.
    """
    if not utc_dt:
        return None
        
    # Ensure the datetime is timezone-aware (UTC)
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    
    target_tz = pytz.timezone(target_tz_str)
    return utc_dt.astimezone(target_tz)
