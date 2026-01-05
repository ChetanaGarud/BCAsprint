import streamlit as st

# --- PAGE CONFIGURATION (Must be the very first command) ---
st.set_page_config(
    page_title="BCAsprint", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- IMPORT MODULES ---
import db_handler
# Import all pages
import preview
import home_page
import runner as salary_module
import hiring_page as hiring_module
import studymaterial as study_module
import Admin as admin_module
import profile_page as profile_module
import notification_page as notification_module

# ==========================================
# 1. GLOBAL STATE INITIALIZATION
# ==========================================

# Initialize DB (Run once)
if 'db_init' not in st.session_state:
    try:
        db_handler.create_table()
        db_handler.ensure_admin()
        st.session_state.db_init = True
    except Exception as e:
        st.error(f"Database Connection Failed: {e}")

# Initialize Session State Variables
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if 'user_info' not in st.session_state: 
    st.session_state.user_info = {"username": "Guest", "role": "user"}

if 'current_page' not in st.session_state: 
    st.session_state.current_page = "Home"

# UI States for Login/Preview
if 'show_login' not in st.session_state: st.session_state.show_login = False
if 'salary_btn_clicked' not in st.session_state: st.session_state.salary_btn_clicked = False
if 'library_btn_clicked' not in st.session_state: st.session_state.library_btn_clicked = False
if 'page' not in st.session_state: st.session_state.page = "login"
if 'signup_pending' not in st.session_state: st.session_state.signup_pending = None
if 'forgot_stage' not in st.session_state: st.session_state.forgot_stage = "request_email"
if 'reset_email' not in st.session_state: st.session_state.reset_email = ""
if 'show_success' not in st.session_state: st.session_state.show_success = False

# ==========================================
# 2. ROUTING ENGINE
# ==========================================

# Logic to handle Email Clicks (e.g., "Did you apply?")
if "action" in st.query_params and st.query_params["action"] == "log_application":
    user = st.query_params.get("user")
    role = st.query_params.get("role")
    status = st.query_params.get("status")
    db_handler.log_job_application(user, role, "External", status)
    st.toast(f"✅ Status updated: {status} for {role}")
    st.query_params.clear()

# MAIN NAVIGATION
if not st.session_state.logged_in:
    # Show Landing Page if not logged in
    preview.show_landing_page()
else:
    # --- FIX FOR OVERLAPPING (Add this block) ---
    # This forces a hard refresh immediately after login to clear Landing Page CSS
    if 'login_refresh_done' not in st.session_state:
        st.session_state.login_refresh_done = True
        st.rerun()
    # --------------------------------------------

    # Logged In Navigation
    page = st.session_state.current_page

    if page == "Home":
        home_page.show_home()
    elif page == "Salary":
        salary_module.show_salary_predictor_page()
    elif page == "Hiring":
        hiring_module.show_hiring_aptitude_page()
    elif page == "Study":
        study_module.study_materials()
    elif page == "Admin":
        admin_module.show_admin_page()
    elif page == "Profile":
        profile_module.show_profile_page()
    elif page == "Notifications":
        notification_module.notify()
    else:
        st.session_state.current_page = "Home"
        st.rerun()