import streamlit as st
import time
import random
import json
import os 
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_handler import ( 
    get_user_by_email, create_user_pending_verification, 
    verify_user, set_otp_for_reset, update_user_password,
    log_login, ensure_admin, create_table
) 

# Ensure tables exist 

# --- Streamlit Lottie Import ---
try:
    from streamlit_lottie import st_lottie
    
    @st.cache_data(ttl=3600)
    def load_lottie_json(filepath: str):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def load_lottie_file(filepath: str):
        return load_lottie_json(filepath)
    
except ImportError:
    def st_lottie(*args, **kwargs):
        st.markdown('<div style="color:#444; text-align:center; padding-top:200px;">Animation Missing (pip install streamlit-lottie)</div>', unsafe_allow_html=True)
    def load_lottie_file(filepath: str): return None


# =========================================================================
# === REAL EMAIL SENDER INTEGRATION =======================================
# =========================================================================
def send_otp_email(to_email: str, otp_code: str, purpose="verification") -> bool:
    """Send OTP email using credentials from .streamlit/secrets.toml."""
    try:
        email_config = st.secrets.get("email", {})
        EMAIL_USER = email_config.get("sender_email")
        EMAIL_PASSWORD = email_config.get("sender_password")
                
        if not EMAIL_USER or not EMAIL_PASSWORD:
            raise ValueError("Email credentials not found in secrets.toml")
        
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        
        if purpose == "verification":
            subject = "BCAsprint: Verify Your Email"
            title = "Email Verification"
            action = "Verify your account"
        else:
            subject = "BCAsprint: Password Reset Request"
            title = "Password Reset"
            action = "Reset your password"
            
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                    <h2 style="color: #020617;">BCAsprint - {title}</h2>
                    <p>Dear User,</p>
                    <p>You requested to {action}.</p>
                    <p>Your verification code is:</p>
                    <div style="text-align: center; padding: 15px; background-color: #e2f0e9; border-radius: 5px; margin: 20px 0;">
                        <span style="font-size: 28px; font-weight: bold; color: #10b981; letter-spacing: 2px;">{otp_code}</span>
                    </div>
                    <p style="font-size: 0.9em; color: #666;">This code is valid for 5 minutes. Do not share it.</p>
                    <p style="margin-top: 30px; font-size: 0.8em; color: #999;">BCAsprint Team</p>
                </div>
            </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        
        return True
    
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False
        
# --- STATE MANAGEMENT ---
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'salary_btn_clicked' not in st.session_state:
    st.session_state.salary_btn_clicked = False
if 'library_btn_clicked' not in st.session_state:
    st.session_state.library_btn_clicked = False
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {'username': 'Guest', 'email': '', 'role': 'guest', 'is_verified': False}
if 'show_about' not in st.session_state:
    st.session_state.show_about = False

# --- CALLBACKS ---
def close_modal_and_reset_states():
    st.session_state.show_login = False
    
    if "page" in st.session_state: del st.session_state.page
    if "signup_pending" in st.session_state: del st.session_state.signup_pending
    if "forgot_stage" in st.session_state: del st.session_state.forgot_stage
    if "reset_email" in st.session_state: del st.session_state.reset_email
    if "reset_otp_sent" in st.session_state: del st.session_state.reset_otp_sent
    if "show_success" in st.session_state: del st.session_state.show_success
    
    st.session_state.salary_btn_clicked = False 
    st.session_state.library_btn_clicked = False

def salary_btn_callback():
    st.session_state.salary_btn_clicked = True
    st.session_state.show_login = True
    st.session_state.page = "login"

def library_btn_callback():
    st.session_state.library_btn_clicked = True
    st.session_state.show_login = True
    st.session_state.page = "login"

def action_btn_callback():
    st.session_state.show_login = True
    st.session_state.page = "login"


# --- HELPER FUNCTIONS ---
def password_issues(pw: str):
    issues = []
    if len(pw) < 8: issues.append("8+ chars")
    if not any(c.islower() for c in pw): issues.append("lowercase")
    if not any(c.isupper() for c in pw): issues.append("uppercase")
    if not any(c.isdigit() for c in pw): issues.append("digit")
    return issues

def check_password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8: score += 1
    else: feedback.append("At least 8 characters")
    
    if any(c.islower() for c in password): score += 1
    else: feedback.append("At least one lowercase letter")
    
    if any(c.isupper() for c in password): score += 1
    else: feedback.append("At least one uppercase letter")
    
    if any(c.isdigit() for c in password): score += 1
    else: feedback.append("At least one digit")
    
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if any(c in special_chars for c in password): score += 1
    else: feedback.append("Consider adding a special character (!@#$% etc.)")
    
    if score <= 2: strength = "weak"
    elif score == 3: strength = "fair"
    elif score == 4: strength = "good"
    else: strength = "strong"
    
    return strength, feedback, score

# --- CSS STYLING FUNCTION ---
def apply_login_page_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        [data-testid="stAppViewContainer"] {
            background: #020617 !important;
            height: 100vh;
            overflow: auto !important; 
        }
        
        * { 
            font-family: 'Inter', sans-serif !important; 
            color: #94a3b8; 
        }
        
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }

        [data-testid="stHeader"], footer, [data-testid="stSidebar"] { display: none; }

        .stTextInput>div>div>input, 
        .stTextInput>div>div>textarea,
        div[data-baseweb="select"] > div {  
            background: #f1f5f9 !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: black !important; 
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 14px !important;
            margin-bottom: 15px !important;
            backdrop-filter: none;
        }
        
        input[type="text"], input[type="email"], input[type="password"] {
            color: black !important;
            -webkit-box-shadow: 0 0 0 1000px #f1f5f9 inset !important; 
        }
        
        .stForm label {
            color: white !important;
            font-weight: 600 !important;
            margin-bottom: 5px !important;
            display: block !important;
        }
        
        .stTextInput>div>div>input::placeholder {
            color: #475569 !important; 
            opacity: 1;
        }
        
        .title-text {
            color: white; 
            font-size: 3rem; 
            font-weight: 800; 
            text-align: left;
            letter-spacing: -0.02em; 
            margin-bottom: 25px;
            text-shadow: none; 
        }
        
        .stButton>button { 
            background-color: white !important; 
            color: black !important;
            border-radius: 99px !important; 
            padding: 0.75rem 2rem !important;
            font-weight: 700 !important; 
            border: none !important; 
            width: 100%;
            margin-bottom: 10px;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            background-color: #60a5fa !important; 
            box-shadow: 0 0 20px rgba(96, 165, 250, 0.5) !important;
            transform: translateY(-2px) !important;
            color: white !important;
        }
        
        .stButton button[kind="secondary"] {
            background-color: #0f172a !important; 
            color: white !important; 
            border: 1px solid #1e293b !important; 
            border-radius: 99px !important; 
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[kind="secondary"]:hover {
            color: #60a5fa !important; 
            border-color: #334155 !important;
            background-color: #1e293b !important; 
            transform: none !important;
            box-shadow: none !important;
        }
        
        .password-strength {
            margin-top: 5px;
            margin-bottom: 10px;
            font-size: 12px;
        }
        .strength-weak { color: #ef4444; } 
        .strength-fair { color: #f59e0b; } 
        .strength-good { color: #10b981; } 
        .strength-strong { color: #34d399; } 
        
        div[data-testid^="stButton"]:has(button[key="native_modal_close_btn"]) button {
            position: absolute !important;
            top: 20px !important;
            right: 20px !important;
            width: 35px !important;
            height: 35px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            background-color: #1e293b !important;
            border: 1px solid #4b5563 !important;
            color: #94a3b8 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            z-index: 1000001 !important;
        }
        div[data-testid^="stButton"]:has(button[key="native_modal_close_btn"]) span {
            font-size: 20px !important; 
            font-weight: 700 !important; 
            line-height: 1 !important; 
            margin-top: -3px; 
        }
        div[data-testid^="stButton"]:has(button[key="native_modal_close_btn"]) button:hover {
            background-color: #334155 !important;
            color: white !important;
            box-shadow: none !important;
            transform: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- MAIN LOGIN PAGE FUNCTION ---
def show_log_page():
    apply_login_page_style()
    
    if "page" not in st.session_state: st.session_state.page = "login"
    if "signup_pending" not in st.session_state: st.session_state.signup_pending = None
    if "show_success" not in st.session_state: st.session_state.show_success = False
    
    if "forgot_stage" not in st.session_state: st.session_state.forgot_stage = "request_email"
    if "reset_email" not in st.session_state: st.session_state.reset_email = ""
    
    col1, col2, col3 = st.columns([3, 0.2, 1.2], gap="small", vertical_alignment="center")

    with col1:
        lottie_json = load_lottie_file("oglog.json")
        if lottie_json:
            st_lottie(lottie_json, speed=1, loop=True, quality="high", height=565, key="login_animation")
        else:
            st.markdown('<div style="color:#444; text-align:center; padding-top:200px;">Animation Missing<br>(oglog.json)</div>', unsafe_allow_html=True)

    with col3:
        st.button("X", key="native_modal_close_btn", on_click=close_modal_and_reset_states, type="secondary", help="")
        
        st.markdown(f'<h1 class="title-text">{st.session_state.page.upper()}</h1>', unsafe_allow_html=True) 

        # --- LOGIN PAGE ---
        if st.session_state.page == "login":
            if st.session_state.show_success:
                st.success("Account created successfully. Please log in.")
                st.session_state.show_success = False
            def handle_login(email, password):
                if not email or not password:
                    st.error("Please enter both email and password.")
                    return
                
                user = get_user_by_email(email)
                
                if user is None:
                    st.error("Email not found.")
                    return
                
                if user.get('is_verified') == 0:
                    st.warning("Account not verified. Please check your email.")
                    st.session_state.signup_pending = {'email': email} 
                    st.session_state.page = "signup"
                    st.rerun()
                    return
                
                import hashlib
                hashed_input = hashlib.sha256(password.encode()).hexdigest()
                
                if hashed_input == user['password']:
                    st.session_state.logged_in = True 
                    st.session_state.user_info = {
                        'username': user['username'], 
                        'email': user['email'], 
                        'role': user['role'],
                        'is_verified': user['is_verified']
                    }
                    log_login(user['username'], user['email']) 
                    close_modal_and_reset_states() 
                else:
                    st.error("Incorrect password. Please try again.")
            with st.form("login_form", clear_on_submit=False):
                st.write("") 
                email = st.text_input("Email", key="login_email_input", placeholder="Enter your email") 
                password = st.text_input("Password", type="password", key="login_password_input", placeholder="Enter your password")
                st.write("")
                submitted = st.form_submit_button("LOGIN") 

            if submitted:
                handle_login(email, password)
            
            def go_to_signup():
                st.session_state.page = "signup"
            def go_to_forgot():
                st.session_state.page = "forgot"
                st.session_state.forgot_stage = "request_email"

            c1, c2 = st.columns([1, 1])
            c1.button("Create Account", key="btn_create", type="secondary", use_container_width=True, on_click=go_to_signup) 
            c2.button("Forgot Password?", key="btn_forgot", type="secondary", use_container_width=True, on_click=go_to_forgot) 

        # --- SIGNUP PAGE ---
        elif st.session_state.page == "signup":
            
            def go_back_to_login():
                st.session_state.page = "login"
                st.session_state.signup_pending = None
            def cancel_signup():
                st.session_state.signup_pending = None
                st.session_state.page = "login"
                
            # SIGNUP STEP 1
            if not st.session_state.signup_pending:
                with st.form("signup"):
                    st.write("Enter your details to create an account.")
                    su_name = st.text_input("Username", placeholder="Choose a username")
                    su_email = st.text_input("Email", placeholder="Enter your email")
                    su_pass = st.text_input("Password", type="password", placeholder="Choose a secure password")
                    su_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm the password")
                    
                    if su_pass:
                        strength, feedback, score = check_password_strength(su_pass)
                        st.markdown(f'<div class="password-strength strength-{strength}">Password strength: {strength.upper()}</div>', unsafe_allow_html=True)
                        if score < 4:
                            for item in feedback[:3]: 
                                st.caption(f"⚠️ {item}")
                    
                    st.write("")
                    submit_send_code = st.form_submit_button("SEND CODE")

                if submit_send_code:
                    if not su_name or not su_email or not su_pass or not su_confirm:
                        st.error("Please fill all required fields.")
                    elif su_pass != su_confirm:
                        st.error("Passwords do not match.")
                    elif password_issues(su_pass):
                            st.error(f"Password not secure enough: {', '.join(password_issues(su_pass))}")
                    elif get_user_by_email(su_email):
                            st.error("This email is already registered.")
                    else:
                        otp = str(random.randint(100000, 999999)) 
                        
                        success_db = create_user_pending_verification(su_name, su_email, su_pass, otp)
                        
                        if success_db:
                            send_success = send_otp_email(su_email, otp, purpose="verification")
                            
                            st.session_state.signup_pending = {
                                "name": su_name, "email": su_email, "password": su_pass
                            }
                            st.rerun() 
                        else:
                            st.error("Failed to create user record. Please try again.")
                        
                st.button("← Back to Login", key="signup_back_btn", type="secondary", use_container_width=True, on_click=go_back_to_login)

            # SIGNUP STEP 2
            else:
                def handle_verify_otp(otp_in):
                  if verify_user(st.session_state.signup_pending['email'], otp_in.strip()): 
                    st.session_state.signup_pending = None
                    st.session_state.show_success = True
                    st.session_state.page = "login"
                    st.rerun()
                  else: 
                    st.error("Invalid or expired verification code.")

                st.info(f"Verification code sent to {st.session_state.signup_pending['email']}. Check your spam folder.")
                
                with st.form("otp_verify_form"):
                    otp_in = st.text_input("Verification Code", max_chars=6, placeholder="6-digit code")
                    submit_verify = st.form_submit_button("VERIFY")

                if submit_verify:
                    handle_verify_otp(otp_in)
                
                col_resend, col_cancel = st.columns([1, 1])
                
                with col_resend:
                    if st.button("Resend Code", type="secondary", use_container_width=True):
                        new_otp = str(random.randint(100000, 999999)) 
                        set_otp_for_reset(st.session_state.signup_pending['email'], new_otp) 
                        send_otp_email(st.session_state.signup_pending['email'], new_otp, purpose="verification")
                        st.info("New code sent.")
                
                with col_cancel:
                    st.button("Cancel", type="secondary", use_container_width=True, on_click=cancel_signup)


        # --- FORGOT PASSWORD PAGE ---
        elif st.session_state.page == "forgot":
            st.markdown("<h5 style='color:white; font-weight:700;'>PASSWORD RECOVERY</h5>", unsafe_allow_html=True)
            
            def go_back_to_login_from_forgot():
                st.session_state.page = "login"
                st.session_state.forgot_stage = "request_email"
            def cancel_forgot():
                st.session_state.page = "login"
                st.session_state.forgot_stage = "request_email"
            
            # STAGE 1: Request Email
            if st.session_state.forgot_stage == "request_email":
                with st.form("forgot_email_form"):
                    email = st.text_input("Registered Email", key="forgot_email", placeholder="Enter your registered email")
                    submit_reset_code = st.form_submit_button("SEND VERIFICATION CODE")

                if submit_reset_code:
                    if email.strip():
                        user = get_user_by_email(email)
                        if user is None:
                            st.error("Email not found in our system.")
                        else:
                            otp = str(random.randint(100000, 999999)) 
                            set_otp_for_reset(email, otp)
                            send_otp_email(email, otp, purpose="password_reset")
                            
                            st.session_state.reset_email = email
                            st.session_state.forgot_stage = "verify_otp"
                            st.rerun() 
                    else:
                        st.error("Please enter your email address.")
                
                st.button("← Back to Login", key="forgot_back_btn", type="secondary", use_container_width=True, on_click=go_back_to_login_from_forgot)
            
            # STAGE 2: Verify OTP
            elif st.session_state.forgot_stage == "verify_otp":
                
                def handle_verify_reset_code(otp_input):
                    if verify_user(st.session_state.reset_email, otp_input): 
                        st.session_state.forgot_stage = "reset_password"
                        st.rerun()
                    else:
                        st.error("Invalid or expired verification code.")

                st.info(f"Verification code sent to {st.session_state.reset_email}")
                
                with st.form("verify_otp_form_stage2"):
                    otp_input = st.text_input("Verification Code", max_chars=6, key="otp_input_stage2", placeholder="6-digit code")
                    submit_otp_verify = st.form_submit_button("VERIFY CODE")
                
                if submit_otp_verify:
                    handle_verify_reset_code(otp_input)
                
                col_resend, col_cancel = st.columns([1, 1])
                
                with col_resend:
                    if st.button("Resend Code", type="secondary", use_container_width=True):
                        new_otp = str(random.randint(100000, 999999)) 
                        set_otp_for_reset(st.session_state.reset_email, new_otp)
                        send_otp_email(st.session_state.reset_email, new_otp, purpose="password_reset")
                        st.info("New code sent.")
                        st.rerun()
                
                with col_cancel:
                    st.button("Cancel", type="secondary", use_container_width=True, on_click=cancel_forgot)
            
            # STAGE 3: Reset Password
            elif st.session_state.forgot_stage == "reset_password":
                
                def handle_reset_password(new_password, confirm_password):
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif password_issues(new_password):
                            st.error(f"Password requirements not met: {', '.join(password_issues(new_password))}")
                    else:
                        if update_user_password(st.session_state.reset_email, new_password):
                            st.success("Password successfully reset! You can now log in.")
                            st.session_state.forgot_stage = "request_email"
                            st.session_state.page = "login"
                            st.rerun() 
                        else:
                            st.error("Failed to update password in database.")

                st.info(f"Setting new password for {st.session_state.reset_email}")
                
                with st.form("reset_password_form"):
                    new_password = st.text_input("New Password", type="password", key="new_password", placeholder="Enter new password")
                    confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password", placeholder="Confirm new password")
                    
                    if new_password:
                        strength, feedback, score = check_password_strength(new_password)
                        st.markdown(f'<div class="password-strength strength-{strength}">Password strength: {strength.upper()}</div>', unsafe_allow_html=True)
                        if score < 4:
                            for item in feedback[:3]:
                                st.caption(f"⚠️ {item}")
                    
                    submit_reset = st.form_submit_button("RESET PASSWORD")
                    
                if submit_reset:
                    handle_reset_password(new_password, confirm_password)
                
                st.button("Cancel", type="secondary", use_container_width=True, on_click=cancel_forgot)


# =========================================================================
# === INJECT CUSTOM CSS ===================================================
# =========================================================================
def inject_custom_css():
    css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #020617 !important; 
        color: #94a3b8;
        overflow-x: hidden !important;
    }
    
    .block-container {
        max-width: 1200px !important;
        padding-left: 2rem !important; padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    .navbar-outer {
        position: fixed; top: 0; left: 0; width: 100%; height: 80px; 
        z-index: 1000; background: rgba(2, 6, 23, 0.7); backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(30, 41, 59, 0.5); display: flex; justify-content: center;
    }
    .navbar-inner {
        width: 100%; max-width: 1200px; padding: 0 2rem;
        display: flex; justify-content: space-between; align-items: center; height: 100%;
    }
    .nav-left { display: flex; align-items: center; gap: 12px; }
    .nav-icon {
        width: 36px; height: 36px; background-color: #1e293b; border: 1px solid #334155;
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        color: white; font-weight: 800; font-size: 18px;
    }
    .nav-text { color: white; font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em; }
    
    .nav-center {
        position: absolute; left: 50%; transform: translateX(-50%);
        background-color: #0f172a; border: 1px solid #1e293b; border-radius: 9999px;
        padding: 8px 30px; display: flex; gap: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .nav-link { color: #ffffff !important; font-size: 0.9rem; font-weight: 500; text-decoration: none; transition: color 0.2s; }
    .nav-link:hover { color: #34d399 !important; }

    .btn-get-started {
        background-color: white; color: black !important;
        padding: 10px 24px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem;
        text-decoration: none; display: flex; align-items: center; gap: 6px; 
        transition: transform 0.2s;
        cursor: pointer;
        border: none;
        font-family: 'Inter', sans-serif;
    }
    .btn-get-started:hover { transform: translateY(-2px); }

    .solid-band {
        position: absolute; 
        width: 100vw; 
        left: 50%; 
        right: 50%; 
        margin-left: -50vw; 
        margin-right: -50vw;
        background-color: #020617; 
        z-index: 0; 
        pointer-events: none;
        background-image: radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 60%);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }
    
    .brown-band {
        position: absolute; 
        width: 100vw; 
        left: 50%; 
        right: 50%; 
        margin-left: -50vw; 
        margin-right: -50vw;
        background-color: #020617; 
        z-index: 0; 
        pointer-events: none;
        background-image: radial-gradient(circle at 50% 100%, rgba(180, 83, 9, 0.2), transparent 60%);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }

    .study-materials-content {
        position: relative;
        z-index: 1; 
    }
    
    .footer-container {
        background: linear-gradient(180deg, #000000 0%, #020617 100%);
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 6rem;
        padding: 4rem 0 2rem 0;
        position: relative;
        width: 100vw;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
    }
    
    .footer-inner {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1.5fr;
        gap: 3rem;
        margin-bottom: 3rem;
    }
    
    .footer-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    
    .footer-logo-icon {
        width: 40px;
        height: 40px;
        background-color: white;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #020617;
        font-weight: 900;
        font-size: 1.5rem;
    }
    
    .footer-logo-text {
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    .footer-tagline {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 2rem;
        max-width: 300px;
    }
    
    .footer-heading {
        color: white;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    
    .footer-links {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    
    .footer-link {
        color: #94a3b8;
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s;
    }
    
    .footer-link:hover {
        color: #34d399;
    }
    
    .ai-tag {
        color: #34d399; font-size: 0.85rem; font-weight: 700;
        letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 1rem;
        display: flex; align-items: center; gap: 8px;
    }
    .ai-tag::before { content: ''; width: 20px; height: 2px; background: #34d399; display: block; }
    
    .section-head { font-size: 3rem; font-weight: 800; color: white; line-height: 1.1; margin-bottom: 1.5rem; }
    .accent-green { color: #34d399; }
    
    .feature-box { display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1.5rem; }
    
    .f-icon {
        width: 48px; height: 48px; 
        background: rgba(52, 211, 153, 0.1); 
        border-radius: 12px; 
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .f-icon svg { stroke: #34d399; width: 24px; height: 24px; }
    .f-content h4 { color: white; font-size: 1.1rem; font-weight: 700; margin: 0 0 4px 0; }
    .f-content p { color: #94a3b8; font-size: 0.95rem; margin: 0; line-height: 1.4; }

    [data-testid="column"] > div:nth-child(2) > div.salary-img-container { 
        height: 100%; 
        display: flex;
        flex-direction: column; 
        justify-content: center; 
    }
    .stImage {
        height: 100%; 
    }
    .stImage > img {
        height: 100%; 
        width: 100%;
        object-fit: cover; 
        mask-image: linear-gradient(to right, transparent 0%, black 20%, black 100%);
        -webkit-mask-image: linear-gradient(to right, transparent 0%, black 20%, black 100%);
    }

    .hero-title { 
        font-size: 6rem; font-weight: 800; line-height: 1.1; color: white; margin-bottom: 1.5rem; letter-spacing: -0.02em; 
    }
    .gradient-text { background: linear-gradient(to right, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-sub { font-size: 1.4rem; color: #94a3b8; line-height: 1.6; max-width: 95%; margin-bottom: 2.5rem; }

    .bento-container { display: grid; grid-template-columns: 1fr 1.3fr; grid-template-rows: 130px 130px; gap: 1rem; }
    .b-card { border-radius: 1.25rem; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.08); display: flex; flex-direction: column; justify-content: center; transition: transform 0.2s; }
    .b-card:hover { transform: translateY(-3px); }
    .card-dark { background-color: #0f172a; }
    .card-blue { background-color: #2563eb; color: white; border: none; }
    
    .c-ai { grid-column: 1; grid-row: 1; }
    .c-alert { grid-column: 1; grid-row: 2; }
    .c-stat { grid-column: 2; grid-row: 1; }
    .c-res { grid-column: 2; grid-row: 2; }
    
    .icon-sm { width: 32px; height: 32px; margin-bottom: 0.8rem; display:flex; align-items:center; }
    .icon-sm svg { width: 100%; height: 100%; stroke-width: 2px; }

    .card-head { font-weight: 700; font-size: 1rem; color: white; margin-bottom: 0.2rem; }
    .card-sub { font-size: 0.75rem; color: #94a3b8; line-height: 1.3; }
    .big-stat { font-size: 2.5rem; font-weight: 800; line-height: 1; margin-bottom: 0.2rem; }
    .stat-sub { font-size: 0.75rem; opacity: 0.9; }

    button[kind="primary"] {
        background-color: white !important; 
        color: black !important;
        border-radius: 99px !important; padding: 0.75rem 2rem !important;
        font-weight: 700 !important; border: none !important; transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #60a5fa !important; 
        box-shadow: 0 0 20px rgba(96, 165, 250, 0.5) !important;
        transform: translateY(-2px) !important;
        color: white !important;
    }

    #salary-button-container .stButton > button {
        background-color: white !important;
        color: black !important;
    }
    
    button[key="apt_btn"] {
        background-color: #3b82f6 !important; 
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }
    button[key="apt_btn"]:hover {
        background-color: #2563eb !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.5) !important;
    }

    .resource-library-tag {
        color: #ffb84d; 
        font-size: 0.85rem; font-weight: 700;
        letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 1.5rem;
        display: flex; align-items: center; gap: 8px;
    }
    .resource-library-tag::before { content: ''; width: 25px; height: 2px; background: #ffb84d; display: block; }

    .aptitude-title {
        font-size: 3.5rem; font-weight: 800; color: white; line-height: 1.1; margin-bottom: 0.5rem; 
        letter-spacing: -0.05em;
    }
    .aptitude-accent { color: #ffb84d; }

    .aptitude-sub {
        font-size: 1.15rem; color: #94a3b8; line-height: 1.6; max-width: 95%; margin-bottom: 2.5rem;
    }

    .topic-button-container {
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 3rem;
    }
    .topic-button {
        background-color: #1e293b; 
        color: white; 
        padding: 1rem; 
        border-radius: 6px; 
        text-align: center; 
        font-weight: 600; 
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .topic-button:hover {
        background-color: #334155;
    }

    #library-button-container .stButton > button {
        background-color: #ffb84d !important; 
        color: #020617 !important; 
        font-size: 1.1rem !important;
        padding: 1rem 3rem !important; 
        border-radius: 8px !important; 
        transition: all 0.2s ease !important;
    }
    #library-button-container .stButton > button:hover {
        background-color: #f97316 !important; 
        box-shadow: 0 0 25px rgba(255, 184, 77, 0.6) !important;
        transform: translateY(-2px) !important;
        color: #020617 !important; 
    }

    header, footer { display: none !important; }
    
    .feature-title { font-size: 2.5rem; font-weight: 800; color: white; margin-bottom: 1rem; line-height: 1.2; }
    .feature-desc { font-size: 1.125rem; color: #94a3b8; line-height: 1.75; margin-bottom: 1.5rem; }
    
    .modal-active [data-testid="stVerticalBlock"]:first-of-type > div:first-child > div:nth-child(2) > div:first-child > div:first-child {
        position: fixed !important; 
        top: 0 !important; 
        left: 0 !important; 
        right: 0 !important; 
        bottom: 0 !important; 
        background: rgba(0, 0, 0, 0.85) !important; 
        backdrop-filter: blur(5px) !important;
        display: flex !important; 
        justify-content: center !important; 
        align-items: center !important;
        z-index: 999999 !important; 
        opacity: 1 !important;
        padding: 0 !important; 
    }
    
    .modal-active [data-testid="stVerticalBlock"]:first-of-type > div:first-child > div:nth-child(2) > div:first-child > div:first-child > div:first-child > div:first-child {
        background: linear-gradient(135deg, #0f0f0f 0%, #000000 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important; 
        border-radius: 20px !important;
        padding: 40px !important;
        width: 90% !important; 
        max-width: 950px !important; 
        max-height: 95vh !important; 
        overflow-y: auto !important; 
        position: relative !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5) !important;
        z-index: 1000000 !important;
        margin: auto !important; 
    }
    
</style>
"""
    
    if not st.session_state.get('logged_in', False) and not st.session_state.show_login:
        css += """
<style>
    [data-testid="stAppViewContainer"] {
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), 
            linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px) !important;
        background-size: 100% 100%, 40px 40px, 40px 40px !important;
        background-attachment: fixed !important;
    }
</style>
"""
    
    if st.session_state.salary_btn_clicked:
        css += """
<style>
#salary-button-container .stButton > button {
    background-color: #34d399 !important;
    color: white !important; 
    transform: none !important;
    box-shadow: 0 0 20px rgba(52, 211, 153, 0.5) !important;
    border-color: #34d399 !important; 
}

#salary-button-container .stButton > button:hover {
    background-color: #10b981 !important;
    transform: translateY(-2px) !important;
    border-color: #10b981 !important;
}
</style>
"""

    if st.session_state.library_btn_clicked:
        css += """
<style>
#library-button-container .stButton > button {
    background-color: #f97316 !important;
    box-shadow: 0 0 25px rgba(255, 184, 77, 0.6) !important;
    transform: none !important;
}
</style>
"""

    if st.session_state.show_login:
        css += """
<style>
    [data-testid="stAppViewContainer"] {
        overflow: hidden !important; 
    }
    html, body {
        overflow: hidden !important;
    }
    .solid-band, .brown-band {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        z-index: -9999 !important;
    }
    [data-testid="stAppViewContainer"] {
        background-image: none !important;
    }
</style>
"""
        st.markdown("""
        <script>
        document.body.classList.add('modal-active');
        </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <script>
        document.body.classList.remove('modal-active');
        </script>
        """, unsafe_allow_html=True)

    st.markdown(css, unsafe_allow_html=True)


# --- 4. LOGIN MODAL FUNCTION ---
def show_login_modal():
    """Display the login modal using a Streamlit container and CSS."""
    modal_container = st.container()
    with modal_container:
        st.markdown("<div class='modal-content-wrapper'>", unsafe_allow_html=True)
        show_log_page()
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# === NEW: ABOUT US MODAL (FLOATING WINDOW) LOGIC =========================
# =========================================================================
def render_about_modal():
    """Renders the About Us modal only if the URL parameter is present."""
    params = st.query_params
    
    # We check if either key exists and equals "true"
    if params.get("show_About") == "true":
 
        
        # We use a raw string (r"") or just ensure no indentation on the lines inside
        html_code = """
<style>
/* --- ANIMATIONS --- */
@keyframes slideUp {
from { transform: translateY(50px); opacity: 0; }
to { transform: translateY(0); opacity: 1; }
}
@keyframes fadeIn {
from { opacity: 0; }
to { opacity: 1; }
}
@keyframes pulse-border {
0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
70% { box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}

/* --- MODAL CONTAINER --- */
.modal-overlay {
position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
background: rgba(0, 0, 0, 0.85); z-index: 999999;
display: flex; justify-content: center; align-items: center;
backdrop-filter: blur(8px);
}

.modal-box {
background: linear-gradient(145deg, #0f172a, #1e293b);
border: 1px solid rgba(255, 255, 255, 0.1);
width: 650px; max-width: 90%; padding: 40px; 
border-radius: 24px;
box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
position: relative;
animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
text-align: left; /* Aligns text for bullet points */
}

/* --- HEADER SECTION --- */
.header-section { text-align: center; margin-bottom: 25px; }
.modal-title { 
font-size: 32px; font-weight: 900; color: white; letter-spacing: -1px; margin: 0;
background: linear-gradient(to right, #60a5fa, #34d399);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.modal-sub { color: #94a3b8; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }

/* --- TEAM BADGE --- */
.team-badge {
background: rgba(59, 130, 246, 0.15);
border: 1px solid rgba(59, 130, 246, 0.3);
color: #93c5fd;
padding: 8px 16px;
border-radius: 99px;
font-size: 0.85rem;
font-weight: 600;
text-align: center;
margin-bottom: 25px;
display: inline-block;
width: 100%;
}

/* --- FEATURE LIST (BULLETS) --- */
.feature-list {
list-style: none;
padding: 0;
margin: 0 0 30px 0;
}
.feature-item {
background: rgba(255, 255, 255, 0.03);
margin-bottom: 12px;
padding: 12px 15px;
border-radius: 12px;
display: flex;
align-items: center;
gap: 15px;
transition: transform 0.2s ease;
border: 1px solid transparent;
animation: fadeIn 0.5s ease forwards;
opacity: 0; /* Starts hidden for animation */
}
.feature-item:hover {
transform: translateX(5px);
border-color: rgba(52, 211, 153, 0.3);
background: rgba(52, 211, 153, 0.05);
}
/* Staggered animation for list items */
feature-item:nth-child(1) { animation-delay: 0.1s; }
.feature-item:nth-child(2) { animation-delay: 0.2s; }
.feature-item:nth-child(3) { animation-delay: 0.3s; }
.feature-item:nth-child(4) { animation-delay: 0.4s; }
.feature-item:nth-child(5) { animation-delay: 0.5s; }

.f-emoji { font-size: 1.2rem; min-width: 30px; text-align: center; }
.f-text { color: #cbd5e1; font-size: 0.95rem; line-height: 1.4; }
.f-bold { color: white; font-weight: 700; color: #34d399; }

/* --- CLOSE BUTTON --- */
.close-btn { 
display: block; width: 100%; padding: 14px; 
background: #ef4444; color: white !important;
border-radius: 12px; text-decoration: none; 
font-weight: 800; text-align: center;
transition: 0.2s; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}
.close-btn:hover { background: #dc2626; transform: translateY(-2px); }

.x-icon { 
position: absolute; top: 20px; right: 25px; 
color: #64748b; font-size: 28px; text-decoration: none; 
transition: 0.2s;
}
.x-icon:hover { color: white; transform: rotate(90deg); }

</style>

<div class="modal-overlay">
<div class="modal-box">
<a href="?" target="_self" class="x-icon">&times;</a>
        
<div class="header-section">
<div class="modal-title"> BCAsprint</div>
<div class="modal-sub">Career Engine for BCA Students</div>
</div>

<div class="team-badge">
 Built by TYBCA Students @ Smt. P.N. Doshi Women's College
</div>

<ul class="feature-list">
<li class="feature-item">
<span class="f-emoji">🔸</span>
<span class="f-text"><span class="f-bold">Hiring Radar:</span> Track upcoming exam dates, registrations, and syllabus patterns.</span>
</li>
<li class="feature-item">
<span class="f-emoji">🔸</span>
<span class="f-text"><span class="f-bold">Smart Salary AI:</span> Predict your market value, compare with industry standards, and get free upskilling course links.</span>
</li>
 <li class="feature-item">
<span class="f-emoji">🔸</span>
<span class="f-text"><span class="f-bold">Job Analysis:</span> Manually analyze any job profile for salary & growth even if not listed.</span>
</li>
<li class="feature-item">
<span class="f-emoji">🔸</span>
<span class="f-text"><span class="f-bold">Job Watchdog:</span> Get real-time email alerts for jobs matching your prediction & track application status.</span>
</li>
<li class="feature-item">
<span class="f-emoji">🔸</span>
<span class="f-text"><span class="f-bold">Secure Access:</span> Verified student accounts via Email OTP & Admin tracking.</span>
</li>
</ul>

</div>
</div>
"""
        st.markdown(html_code, unsafe_allow_html=True)
# =========================================================================
# === MAIN RENDER FUNCTION (THIS NOW CONTAINS THE ENTIRE PAGE LOGIC) ======
# =========================================================================
def show_landing_page():
    # 1. CHECK AND RENDER ABOUT MODAL IF NEEDED
    render_about_modal()

    # Apply CSS before rendering content
    inject_custom_css()

    # Show modal if state is True
    if st.session_state.show_login:
        show_login_modal()
        st.stop()
        
    # --- ANCHORS & NAVBAR ---
    st.markdown('<div id="hero"></div>', unsafe_allow_html=True)

    # NAVBAR HTML
    st.markdown("""
    <div class="navbar-outer">
    <div class="navbar-inner">
    <div class="nav-left">
    <div class="nav-icon">B</div>
    <div class="nav-text">BCAsprint</div>
    </div>
    <div class="nav-center">
    <a href="#salary" class="nav-link">Salary Predictor</a>
    <a href="#aptitude" class="nav-link">Aptitude</a>
    <a href="#materials" class="nav-link">Study Materials</a>
    </div>
    <div>
    """, unsafe_allow_html=True)

    # Conditional Navbar Buttons
    if st.session_state.logged_in:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px;">
        <span style="color: #34d399; font-weight: 600;">Welcome, {st.session_state.user_info['username']}!</span>
        <button class="btn-get-started" onclick="window.parent.postMessage({{'type': 'showLogin'}}, '*')" 
            style="background-color: #0f172a; color: white !important; border: 1px solid #334155;">
            Dashboard →
        </button>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    </div>
    </div>
    </div>
    <div style="height: 120px;"></div>
    """, unsafe_allow_html=True)

    # JavaScript for Get Started button
    st.markdown("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'showLogin') {
            const params = new URLSearchParams(window.location.search);
            params.set('show_login', 'true');
            window.location.search = params.toString();
        }
    });
    </script>
    """, unsafe_allow_html=True)


    # --- HERO SECTION ---
    col1, col2 = st.columns([1, 1], gap="large") 

    with col1:
        st.markdown("""
    <div style="padding-top: 1rem;">
    <h1 class="hero-title">
    Career Growth<br>
    <span class="gradient-text">Engineered by AI</span>
    </h1>
    <p class="hero-sub">
    BCAsprint gives you the advantage to
    Predict your salary, track hiring drives, and access 
    study material links in one unified platform.
    </p>
    </div>
    """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1.5])
        with c1:
            st.button("Launch App  →", type="primary", on_click=action_btn_callback, key="launch_app_btn")

    with col2:
        st.markdown("""
    <div class="bento-container">
    <div class="b-card card-dark c-ai">
    <div class="icon-sm">
        <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path>
        <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path>
        <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path>
        <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path>
        </svg>
    </div>
    <div class="card-head">AI Salary</div>
    <div class="card-sub">Precision market estimates.</div>
    </div>

    <div class="b-card card-blue c-stat">
    <div class="big-stat">91%</div>
    <div class="stat-sub">Accuracy Rate using RandomForest.</div>
    </div>

    <div class="b-card card-dark c-alert">
    <div class="icon-sm">
        <svg viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
    </div>
    <div class="card-head">Instant Alerts</div>
    <div class="card-sub">Never miss an exam.</div>
    </div>

    <div class="b-card card-dark c-res">
    <div class="icon-sm">
        <svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
    </div>
    <div class="card-head">Resources</div>
    <div class="card-sub">Curated study links.</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # --- SALARY INTELLIGENCE ---
    st.markdown('<div id="salary" style="padding-top: 4rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="solid-band" style="height: 650px;"></div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([1, 1], gap="large")

    with col_s1:
        st.markdown("""
    <div class="ai-section" style="padding-top: 2rem;">
    <div class="ai-tag">AI ANALYSIS</div>
    <h2 class="section-head">Know Your <span class="accent-green">True Worth</span></h2>
    <p class="hero-sub" style="font-size:1rem; margin-bottom:2rem;">
    Stop guessing. Our advanced AI analyzes real-time market data to provide 
    accurate salary predictions tailored to your role, skills, and location.
    </p>
    <div class="feature-box">
    <div class="f-icon">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
    <polyline points="17 6 23 6 23 12"></polyline>
    </svg>
    </div>
    <div class="f-content">
    <h4>Market Trends</h4>
    <p>Real-time industry benchmarks.</p>
    </div>
    </div>
    <div class="feature-box">
    <div class="f-icon">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
    </svg>
    </div>
    <div class="f-content">
    <h4>Skill Analysis</h4>
    <p>Value of your specific stack.</p>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
        
        st.markdown('<div id="salary-button-container">', unsafe_allow_html=True)
        st.button(
            "Predict My Salary  →", 
            key="sal_btn", 
            type="primary", 
            on_click=salary_btn_callback
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_s2:
        st.markdown('<div class="salary-img-container">', unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71", width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    # --- HIRING RADAR SECTION ---
    st.markdown('<div id="aptitude" style="padding-top: 6rem;"></div>', unsafe_allow_html=True)

    col_a1, col_a2 = st.columns([1, 1], gap="large")

    with col_a1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2426&auto=format&fit=crop", width='stretch')

    with col_a2:
        st.markdown("""<div style="padding-left: 1rem;">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
    <div style="width: 25px; height: 2px; background-color: #3b82f6;"></div>
    <span style="color: #60a5fa; font-size: 1rem; font-weight: 700; text-transform: uppercase;">Opportunity Radar</span>
    </div>
    <h2 style="font-size: 3.5rem; font-weight: 800; color: white; line-height: 1.1; margin-bottom: 1.5rem;">
    Never Miss A <br>
    <span style="color: #60a5fa;">Hiring Drive</span>
    </h2>
    <p style="color: #94a3b8; font-size: 1.1rem; line-height: 1.6; margin-bottom: 2.5rem; max-width: 90%;">
    Your personalized command center for recruitment exams. Get real-time notifications 
    for top-tier company drives and aptitude tests.
    </p>
    <ul style="list-style: none; padding: 0; margin: 0 0 3rem 0; display: flex; flex-direction: column; gap: 1.2rem;">
    <li style="display: flex; align-items: center; gap: 12px; color: #e2e8f0; font-size: 1rem; font-weight: 500;">
    <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px; color: #3b82f6; min-width: 20px;">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="16 9 12 15 8 12"></polyline>
    </svg>
    Instant notifications for new job openings
    </li>
    <li style="display: flex; align-items: center; gap: 12px; color: #e2e8f0; font-size: 1rem; font-weight: 500;">
    <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px; color: #3b82f6; min-width: 20px;">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="16 9 12 15 8 12"></polyline>
    </svg>
    Detailed exam patterns and syllabus
    </li>
    <li style="display: flex; align-items: center; gap: 12px; color: #e2e8f0; font-size: 1rem; font-weight: 500;">
    <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px; color: #3b82f6; min-width: 20px;">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="16 9 12 15 8 12"></polyline>
    </svg>
    Application deadline reminders
    </li>
    <li style="display: flex; align-items: center; gap: 12px; color: #e2e8f0; font-size: 1rem; font-weight: 500;">
    <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 20px; height: 20px; color: #3b82f6; min-width: 20px;">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="16 9 12 15 8 12"></polyline>
    </svg>
    Eligibility criteria checker
    </li>
    </ul>
    </div>""", unsafe_allow_html=True)
        
        st.button("View Upcoming Aptitude", key="apt_btn", type="primary", on_click=action_btn_callback)

    # --- STUDY MATERIALS ---
    st.markdown('<div id="materials" style="padding-top: 6rem;"></div>', unsafe_allow_html=True) 
    st.markdown('<div class="brown-band" style="height: 600px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="study-materials-content">', unsafe_allow_html=True)

    with st.container():
        col_m1, col_m2 = st.columns(2, gap="large")

        with col_m1:
            st.markdown("""
    <div style="padding-top: 2rem;">
    <div class="resource-library-tag">Resource Library</div>
    <h2 class="aptitude-title">Master Every <br><span class="aptitude-accent">Aptitude Topic</span></h2>
    <p class="aptitude-sub">
    Stop searching aimlessly. We've curated the external resources into one organized library.
    </p>
    <div class="topic-button-container">
        <div class="topic-button">Quantitative</div>
        <div class="topic-button">Logical Reasoning</div>
        <div class="topic-button">Verbal Ability</div>
    </div>
    </div>
    """, unsafe_allow_html=True)
            
            st.markdown('<div id="library-button-container">', unsafe_allow_html=True)
            st.button(
                "Access Library →", 
                key="lib_btn",
                type="primary", 
                on_click=library_btn_callback
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col_m2:
            st.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173", width='stretch')

    st.markdown('</div>', unsafe_allow_html=True)
    # --- FOOTER SECTION ---
    st.markdown("""
    <div class="footer-container">
        <div class="footer-inner">
            <div class="footer-grid">
                <div>
                    <div class="footer-logo">
                        <div class="footer-logo-icon">B</div>
                        <div class="footer-logo-text">BCAsprint</div>
                    </div>
                    <p class="footer-tagline">
                        Empowering Careers with AI-Driven Insights
                    </p>
                </div>
                <div>
                    <div class="footer-links">
                        <a href="#salary" class="footer-link">Salary Predictor</a>
                        <a href="#aptitude" class="footer-link">Aptitude Tracker</a>
                        <a href="#materials" class="footer-link">Study Materials</a>
                    </div>
                </div>
                <div>
                    <div class="footer-links">
                        <a href="?show_About=true" target="_self" class="footer-link">About Us</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    

    # Prevent extra whitespace
    st.markdown("""
    <style>
        .footer-container {
            margin-bottom: 0 !important;
            padding-bottom: 2rem !important;
        }
        
        .block-container {
            padding-bottom: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)