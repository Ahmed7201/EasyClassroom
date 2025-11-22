import os
import streamlit as st
import extra_streamlit_components as stx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json
from datetime import datetime, timedelta

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
    """Singleton cookie manager to avoid duplicate key errors"""
    if 'cookie_manager' not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager()
    return st.session_state.cookie_manager

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
    # Note: Cookie manager needs to be ready before we can read cookies
    token_cookie = cookie_manager.get('classroom_token')
    
    if token_cookie and token_cookie != 'null':
        try:
            # Reconstruct credentials from cookie
            token_data = json.loads(token_cookie)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            
            if creds.valid:
                st.session_state.credentials = creds
                return creds
            
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    st.session_state.credentials = creds
                    # Update cookie with refreshed token (30 days expiry)
                    cookie_manager.set('classroom_token', creds.to_json(), expires_at=datetime.now() + timedelta(days=30), key="refresh_cookie")
                    return creds
                except:
                    # Refresh failed, clear invalid cookie
                    pass
        except Exception as e:
            # Invalid cookie, ignore it
            pass

    # 4. If not logged in, handle OAuth flow
    if 'credentials' not in st.session_state:
        # Check if we're returning from OAuth (code in URL)
        query_params = st.query_params
        
        if 'code' in query_params:
            # Step 2: Exchange code for token
            auth_code = query_params['code']
            
            # Recreate flow to exchange code
            if os.path.exists('credentials.json'):
                flow = Flow.from_client_secrets_file(
                    'credentials.json',
                    scopes=SCOPES,
                    redirect_uri=st.query_params.get('redirect_uri', 'http://localhost:8501')
                )
            elif 'google_credentials' in st.secrets:
                client_config = json.loads(st.secrets['google_credentials'])
                # Detect Streamlit Cloud URL
                redirect_uri = f"https://{st.context.headers.get('Host', 'localhost:8501')}"
                flow = Flow.from_client_config(
                    client_config,
                    scopes=SCOPES,
                    redirect_uri=redirect_uri
                )
            else:
                st.error("❌ Missing Credentials!")
                st.stop()
            
            
            try:
                # Clear query params FIRST to prevent reuse
                auth_code_copy = auth_code
                st.query_params.clear()
                
                flow.fetch_token(code=auth_code_copy)
                creds = flow.credentials
                
                # Save to Session
                st.session_state.credentials = creds
                
                # Save to Cookie (Remember Me - 30 days)
                cookie_manager = get_cookie_manager()
                cookie_manager.set('classroom_token', creds.to_json(), expires_at=datetime.now() + timedelta(days=30), key="new_token")
                
                st.success("✅ Successfully signed in!")
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
                st.stop()
        
        else:
            # Step 1: Show login button
            st.markdown("""
            <div style="text-align: center; margin-top: 50px;">
                <h2>👋 Welcome to EasyClassroom</h2>
                <p>Please sign in to access your courses.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create Flow with proper redirect URI
            if os.path.exists('credentials.json'):
                redirect_uri = 'http://localhost:8501'
                flow = Flow.from_client_secrets_file(
                    'credentials.json',
                    scopes=SCOPES,
                    redirect_uri=redirect_uri
                )
            elif 'google_credentials' in st.secrets:
                # Detect Streamlit Cloud URL
                try:
                    host = st.context.headers.get('Host', '')
                    redirect_uri = f"https://{host}" if host else "http://localhost:8501"
                except:
                    redirect_uri = "http://localhost:8501"
                
                client_config = json.loads(st.secrets['google_credentials'])
                flow = Flow.from_client_config(
                    client_config,
                    scopes=SCOPES,
                    redirect_uri=redirect_uri
                )
            else:
                st.error("❌ Missing Credentials! Please add 'google_credentials' to Streamlit Secrets.")
                st.stop()
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.link_button("🔐 Sign in with Google", auth_url, use_container_width=True)
                st.caption("Click the button above to sign in")
            
        st.stop() # Stop execution until logged in


    return None
