import requests
import streamlit as st
from config import get_setting

def render_turnstile_widget():
    """Render Cloudflare Turnstile CAPTCHA widget in HTML"""
    turnstile_site_key = get_setting("TURNSTILE_SITE_KEY")
    
    if not turnstile_site_key:
        st.warning("⚠️ Turnstile CAPTCHA not configured")
        return None
    
    html_code = f"""
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <div class="cf-turnstile" data-sitekey="{turnstile_site_key}" data-theme="dark"></div>
    """
    
    st.markdown(html_code, unsafe_allow_html=True)
    return turnstile_site_key

def verify_turnstile_token(token):
    """Verify Turnstile token with Cloudflare"""
    try:
        turnstile_secret_key = get_setting("TURNSTILE_SECRET_KEY")
        
        if not turnstile_secret_key:
            st.warning("⚠️ Turnstile secret key not configured")
            return False
        
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": turnstile_secret_key,
                "response": token
            },
            timeout=10
        )
        
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        st.error(f"❌ Turnstile verification failed: {str(e)}")
        return False

def get_turnstile_widget_html():
    """Get HTML for Turnstile widget"""
    turnstile_site_key = get_setting("TURNSTILE_SITE_KEY")
    
    if not turnstile_site_key:
        return ""
    
    return f"""
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <style>
        .turnstile-container {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
        .cf-turnstile {{
            transform: scale(1);
            transform-origin: 0 0;
        }}
    </style>
    <div class="turnstile-container">
        <div class="cf-turnstile" data-sitekey="{turnstile_site_key}" data-theme="dark"></div>
    </div>
    """