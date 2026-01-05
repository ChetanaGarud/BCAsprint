import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import PyPDF2
import re
import time
import db_handler as db  # To log the "Did you apply" actions later

# ==========================================
# 1. CSS STYLING
# ==========================================
def inject_notification_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400&display=swap');
    
    .stApp { font-family: 'Outfit', sans-serif; }

    /* Command Center Header */
    .cmd-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    .cmd-title { 
        font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-bottom: 5px; 
        background: linear-gradient(to right, #F8FAFC, #94A3B8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    /* Logic Cards */
    .logic-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .logic-card.active { border-color: #00B4D8; background: rgba(0, 180, 216, 0.05); }
    
    .step-badge {
        background: #334155; color: #94A3B8; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;
    }
    .active .step-badge { background: #00B4D8; color: white; }

    /* Console */
    .console-box {
        background-color: #000000;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        font-family: 'JetBrains Mono', monospace;
        color: #00E676;
        font-size: 0.9rem;
        margin-top: 20px;
        max-height: 300px;
        overflow-y: auto;
    }
    .log-entry { margin-bottom: 5px; border-bottom: 1px dashed #333; padding-bottom: 2px; }
    
    /* Input Overrides */
    .stTextInput input { background-color: #1e293b !important; color: white !important; border: 1px solid #475569 !important; }
    
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
        color: white; border: none; font-weight: 700; width: 100%;
        padding: 0.8rem; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Specific style for the small Home button to override the large button style above */
    div[data-testid="stButton"] button[key="nav_home_notification"] {
        background: transparent !important;
        border: 1px solid #334155 !important;
        color: #00B4D8 !important;
        width: auto !important;
        padding: 0.4rem 1rem !important;
        margin-bottom: 10px;
    }
    div[data-testid="stButton"] button[key="nav_home_notification"]:hover {
        border-color: #00B4D8 !important;
        background: rgba(0, 180, 216, 0.1) !important;
    }

    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ANALYSIS LOGIC
# ==========================================
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception:
        return ""

def analyze_profile_smart(resume_text, manual_role, manual_loc):
    """
    Priority Logic:
    1. Resume (High Accuracy)
    2. Salary Predictor History (Medium Accuracy)
    3. Manual Input (User Defined)
    """
    
    # 1. RESUME CHECK
    if resume_text:
        bca_skills = ["Python", "Java", "SQL", "React", "Node", "Data Analyst", "Testing", "Support", "Network", "Linux"]
        found = []
        for skill in bca_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE):
                found.append(skill)
        
        role = f"{found[0]} Developer" if found else "Freshers"
        # If manual location is provided in Step 3, use it, otherwise default to India
        loc = manual_loc if manual_loc else "India"
        return f"{role} jobs in {loc}", "📄 Resume Analysis", found

    # 2. SALARY PREDICTOR CHECK
    #elif 'prediction_results' in st.session_state and st.session_state.prediction_results:
     #   inputs = st.session_state.prediction_results.get("input_row", {})
      #  role = inputs.get("Job_Role_Level", "").split(" - ")[0]
       # loc = inputs.get("District", "")
        #return f"{role} jobs in {loc}", "🤖 Prediction History", [role, loc]

    # 3. MANUAL INPUT CHECK
    elif manual_role and manual_loc:
        return f"{manual_role} jobs in {manual_loc}", "✍️ Manual Input", [manual_role]

    # 4. FAILURE
    else:
        return None, None, None

# ==========================================
# 3. EMAIL LOGIC
# ==========================================
def send_global_scout_email(user_email, user_name, query, source):
    try:
        EMAIL_USER = st.secrets["email"]["sender_email"]
        EMAIL_PASS = st.secrets["email"]["sender_password"]
        app_url = "http://localhost:8501"
        
        # 1. Generate Search URLs
        q_enc = urllib.parse.quote(query)
        
        links = {
            "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={q_enc}",
            "Naukri": f"https://www.naukri.com/{q_enc.replace('%20', '-')}",
            "Indeed": f"https://in.indeed.com/jobs?q={q_enc}",
            "Google Jobs": f"https://www.google.com/search?q={q_enc}&ibp=htl;jobs"
        }

        # 2. Generate Tracking Links
        # We log 'Applied' or 'Helpful' clicks
        track_apply = f"{app_url}/?action=log_application&status=Applied&role={q_enc}&user={user_name}"
        track_helpful = f"{app_url}/?action=log_application&status=Helpful&role={q_enc}&user={user_name}"

        # 3. Email Body
        links_html = ""
        for site, url in links.items():
            links_html += f"""
            <a href="{url}" style="display:block; background:#f8fafc; padding:12px; margin:8px 0; border:1px solid #e2e8f0; border-radius:6px; text-decoration:none; color:#334155; font-weight:bold;">
                Search on {site} &rarr;
            </a>
            """

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = user_email
        msg['Subject'] = f"🐕 Watchdog Report: {query}"
        
        body = f"""
        <html>
        <body style="font-family: sans-serif; padding: 20px; color: #333; max-width: 600px; margin: auto;">
            <div style="text-align: center; border-bottom: 2px solid #00B4D8; padding-bottom: 20px;">
                <h2 style="color: #00B4D8; margin:0;">GLOBAL JOB SCOUT</h2>
                <p style="color: #64748b;">Source: {source}</p>
            </div>

            <p>Hi {user_name},</p>
            <p>We scanned the entire web for <b>"{query}"</b>. Here are the direct search results across all major platforms:</p>
            
            {links_html}

            <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="text-align: center; font-size: 14px; font-weight: bold;">Quick Feedback (Updates your Dashboard)</p>
            <div style="text-align: center;">
                <a href="{track_apply}" style="background-color: #2ecc71; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">✅ I Applied</a>
                <a href="{track_helpful}" style="background-color: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">👍 Just Helpful</a>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# ==========================================
# 4. MAIN UI
# ==========================================
def notify():
    inject_notification_css()
    
    # --- NAVIGATION BUTTON ---
    col_nav, col_title = st.columns([1, 5])
    with col_nav:
        if st.button("← Home", key="nav_home_notification"):
            st.session_state.current_page = "Home"
            st.rerun()

    # --- HEADER ---
    st.markdown("""
        <div class="cmd-header">
            <div class="cmd-title">⚡ GLOBAL WATCHDOG</div>
            <div class="cmd-sub">Intelligent Cross-Platform Job Scout</div>
        </div>
    """, unsafe_allow_html=True)

    # --- STEP 1: RESUME ---
    resume = None
    has_prediction = 'prediction_results' in st.session_state and st.session_state.prediction_results
    
    # UI Logic for Active State
    step1_active = "active"
    step2_active = "active" if not resume and has_prediction else ""
    step3_active = "active" if not resume and not has_prediction else ""

    # 1. RESUME UPLOAD
    st.markdown(f"""
    <div class="logic-card {step1_active}">
        <span class="step-badge">PRIORITY 1</span>
        <h4 style="margin:5px 0; color:#F8FAFC;">📄 Resume Analysis</h4>
        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:10px;">
            Upload your PDF resume. AI will extract your top skills to find relevant jobs.
        </div>
    </div>
    """, unsafe_allow_html=True)
    resume = st.file_uploader("Upload Resume", type=["pdf"], key="global_resume", label_visibility="collapsed")

    # 2. PREDICTION DATA
    #if not resume:
         #st.markdown(f"""
         #<div class="logic-card {step2_active}">
             #<span class="step-badge">PRIORITY 2</span>
            # <h4 style="margin:5px 0; color:#F8FAFC;">🤖 Prediction History</h4>
            # <div style="font-size:0.85rem; color:#94A3B8;">
            # #     {'✅ Data Found' if has_prediction else '❌ No Salary Prediction Data Found'}
           #  </div>
         #</div>
        # """, unsafe_allow_html=True)

    # 3. MANUAL INPUT
    manual_role = ""
    manual_loc = ""
    
    if not resume and not has_prediction:
        st.markdown(f"""
        <div class="logic-card {step3_active}">
            <span class="step-badge">PRIORITY 3</span>
            <h4 style="margin:5px 0; color:#F8FAFC;">✍️ Manual Configuration</h4>
            <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:10px;">
                Since we have no data, tell us what you are looking for.
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: manual_role = st.text_input("Target Job Role", placeholder="e.g. Java Developer")
        with c2: manual_loc = st.text_input("Preferred Location", placeholder="e.g. Pune")

    # --- ACTION BUTTON ---
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    if st.button("🚀 DEPLOY WATCHDOG AGENT"):
        user_email = st.session_state.user_info.get('email')
        user_name = st.session_state.user_info.get('username')

        if not user_email:
            st.error("Please login to use this feature.")
        else:
            # Analyze inputs
            raw_text = extract_text_from_pdf(resume) if resume else None
            query, source, tags = analyze_profile_smart(raw_text, manual_role, manual_loc)

            if query:
                # CONSOLE ANIMATION
                console = st.empty()
                logs = []
                def log(msg):
                    ts = time.strftime("%H:%M:%S")
                    logs.append(f"<div class='log-entry'><span class='log-time'>[{ts}]</span> {msg}</div>")
                    console.markdown(f"<div class='console-box'>{''.join(logs)}</div>", unsafe_allow_html=True)
                    time.sleep(0.6)

                log("Initializing Watchdog v2.0...")
                log(f"Data Source Identified: {source}")
                if tags: log(f"Keywords Extracted: {', '.join(tags)}")
                log(f"Constructed Query: '{query}'")
                log("Scanning global job aggregators (LinkedIn, Naukri, Indeed)...")
                log(f"Compiling intelligence report for {user_email}...")
                
                if send_global_scout_email(user_email, user_name, query, source):
                    log("✅ INTELLIGENCE DISPATCHED SUCCESSFULLY.")
                    st.toast("Check your email!", icon="📩")
                else:
                    log("❌ SMTP HANDSHAKE FAILED. Check secrets.")
            else:
                st.error("⚠️ Input Missing: Please upload a resume, use the predictor, or fill manual details.") 