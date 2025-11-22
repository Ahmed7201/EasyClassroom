import os
import streamlit as st
import extra_streamlit_components as stx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json

# Relax scope validation
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Scopes
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar'
]

def get_cookie_manager():
    return stx.CookieManager()

def authenticate():
    """
    Handles authentication for Web Deployment.
    Uses Cookies to persist login across sessions.
    """
    
    # 1. Initialize Cookie Manager
    cookie_manager = get_cookie_manager()
    
    # 2. Check Session State (Already logged in this tab?)
    if 'credentials' in st.session_state:
        creds = st.session_state.credentials
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                st.session_state.credentials = creds
                # Update cookie if refreshed
                cookie_manager.set('classroom_token', creds.to_json(), key="set_token")
                return creds
            except:
                st.session_state.credentials = None

    # 3. Check Cookies (Remember Me)
    # Note: We store the full token JSON in the cookie for simplicity in this "Universal" app.
    # In a high-security production app, we would store a session ID and keep tokens in a DB.
    token_cookie = cookie_manager.get('classroom_token')
    
    if token_cookie:
        try:
            # Reconstruct credentials from cookie
            token_data = json.loads(token_cookie)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            
            if creds.valid:
                st.session_state.credentials = creds
                return creds
            
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                st.session_state.credentials = creds
                cookie_manager.set('classroom_token', creds.to_json(), key="refresh_cookie")
                return creds
        except Exception as e:
            # Invalid cookie, clear it
            # cookie_manager.delete('classroom_token') # Can be buggy in some versions
            pass

    # 4. If not logged in, show Login Button
    if 'credentials' not in st.session_state:
        st.markdown("""
        <div style="text-align: center; margin-top: 50px;">
            <h2>👋 Welcome to Classroom Assistant</h2>
            <p>Please sign in to access your courses.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create Flow
        if os.path.exists('credentials.json'):
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
        elif 'google_credentials' in st.secrets:
            # Load from Streamlit Secrets (for Cloud Deployment)
            client_config = json.loads(st.secrets['google_credentials'])
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
        else:
            st.error("❌ Missing Credentials! Please upload 'credentials.json' or add 'google_credentials' to Streamlit Secrets.")
            st.stop()
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.link_button("🔐 Sign in with Google", auth_url, use_container_width=True)
            
            auth_code = st.text_input("Paste the code from Google here:", type="password")
            
            if auth_code:
                try:
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    
                    # Save to Session
                    st.session_state.credentials = creds
                    
                    # Save to Cookie (Remember Me)
                    cookie_manager.set('classroom_token', creds.to_json(), key="new_token")
                    
                    st.success("Successfully signed in! Reloading...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {str(e)}")
                    
        st.stop() # Stop execution until logged in

    return None
