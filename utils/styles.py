import streamlit as st

def load_css(theme='dark'):
    """Load CSS with theme support (dark or light)"""
    
    if theme == 'light':
        # Light Theme CSS - "Modern Ocean" Identity
        st.markdown("""
        <style>
            /* Global Font & Background */
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Outfit', sans-serif;
            }

            /* Main App Background - Soft Cool Gray */
            .stApp {
                background-color: #f0f2f5 !important;
                color: #1a202c !important;
            }
            
            [data-testid="stAppViewContainer"] {
                background-color: #f0f2f5 !important;
            }
            
            /* Main content area */
            .main {
                background-color: #f0f2f5 !important;
            }

            /* Glassmorphism Card Style - Light Mode Redesign */
            .glass-card {
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid rgba(226, 232, 240, 0.8);
                padding: 24px;
                margin-bottom: 20px;
                /* Stronger shadow for better contrast against light bg */
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease;
            }
            
            .glass-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                border-color: #3b82f6; /* Bright Blue on hover */
            }

            /* Headers - Deep Navy for Contrast */
            h1, h2, h3 {
                color: #1e3a8a !important; /* Blue 900 */
                font-weight: 800;
                letter-spacing: -0.5px;
            }
            
            h4, h5, h6 {
                color: #0284c7 !important; /* Light Blue 600 */
                font-weight: 600;
            }

            /* Custom Buttons - Vibrant Ocean Gradient */
            .stButton>button {
                background: linear-gradient(135deg, #2563eb 0%, #0891b2 100%); /* Blue to Cyan */
                color: white !important;
                border: none;
                border-radius: 12px;
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                background: linear-gradient(135deg, #1d4ed8 0%, #0e7490 100%);
                box-shadow: 0 8px 15px rgba(37, 99, 235, 0.3);
                transform: translateY(-1px);
            }

            /* Sidebar - Crisp White */
            [data-testid="stSidebar"] {
                background-color: #ffffff;
                border-right: 1px solid #e5e7eb;
            }
            
            /* Sidebar Text Fixes */
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
                color: #374151 !important;
            }

            /* Metrics - Vibrant Gradient Text */
            [data-testid="stMetricValue"] {
                font-size: 2.5rem;
                font-weight: 700;
                background: -webkit-linear-gradient(135deg, #2563eb, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            [data-testid="stMetricLabel"] {
                color: #64748b !important; /* Slate 500 */
            }
            
            /* Progress Bars */
            .stProgress > div > div > div > div {
                background-image: linear-gradient(to right, #2563eb, #06b6d4);
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                color: #1f2937 !important;
            }
            
            /* General Text Contrast */
            p, span, div, label {
                color: #334155; /* Slate 700 - Softer than black, readable */
            }
            
            /* Input fields */
            .stSelectbox > div > div {
                background-color: #ffffff;
                color: #1f2937;
                border-color: #e5e7eb;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Dark Theme CSS (original)
        st.markdown("""
        <style>
            /* Global Font & Background */
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Outfit', sans-serif;
            }

            /* Glassmorphism Card Style */
            .glass-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .glass-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(189, 147, 249, 0.3);
            }

            /* Headers */
            h1, h2, h3 {
                color: #bd93f9 !important; /* Dracula Purple */
                font-weight: 700;
                letter-spacing: -0.5px;
            }
            
            h4, h5, h6 {
                color: #8be9fd !important; /* Dracula Cyan */
            }

            /* Custom Buttons */
            .stButton>button {
                background: linear-gradient(135deg, #6272a4 0%, #44475a 100%);
                color: white;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 0.5rem 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                background: linear-gradient(135deg, #bd93f9 0%, #6272a4 100%);
                box-shadow: 0 0 15px rgba(189, 147, 249, 0.4);
                border-color: #bd93f9;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: #21222c;
                border-right: 1px solid rgba(255,255,255,0.05);
            }

            /* Metrics */
            [data-testid="stMetricValue"] {
                font-size: 2.5rem;
                font-weight: 700;
                background: -webkit-linear-gradient(#ff79c6, #bd93f9);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            /* Progress Bars */
            .stProgress > div > div > div > div {
                background-image: linear-gradient(to right, #bd93f9, #ff79c6);
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                background-color: rgba(255,255,255,0.02);
                border-radius: 8px;
            }
        </style>
        """, unsafe_allow_html=True)

def card(title, content, footer=None, color="white"):
    """Helper to render a glassmorphism card"""
    footer_html = f"<div style='margin-top:15px; font-size:0.8em; opacity:0.7;'>{footer}</div>" if footer else ""
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="margin-top:0; font-size:1.2rem; color:{color} !important;">{title}</h3>
        <div style="font-size:1rem; line-height:1.5;">{content}</div>
        {footer_html}
    </div>
    """, unsafe_allow_html=True)

