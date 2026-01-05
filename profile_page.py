import streamlit as st
import time

# --- PAGE CONFIGURATION ---
# Note: If this is a sub-page, ensure set_page_config is only called once in your main app.
st.set_page_config(
    page_title="My Profile - Career Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def show_profile_page():
    # --- 1. DATA SETUP: CAREER PERSONAS ---
    archetypes = {
        "G.ONE": {
            "icon": "🛡️", 
            "role": "The Protector",
            "desc": "I am interested in AI, Cybersecurity & Defense.", 
            "color": "#00f3ff" # Cyan
        },
        "RA.ONE": {
            "icon": "☣️", 
            "role": "The Destroyer",
            "desc": "I enjoy Ethical Hacking, Testing & finding Bugs.", 
            "color": "#ff0055" # Red
        },
        "LUCIFER": {
            "icon": "🎮", 
            "role": "The Gamer",
            "desc": "I excel at Logic, Algorithms & Problem Solving.", 
            "color": "#facc15" # Yellow
        },
        "GENESIS": {
            "icon": "💠", 
            "role": "The Creator",
            "desc": "I love System Design, UI/UX & Architecture.", 
            "color": "#a855f7" # Purple
        }
    }

    # Initialize Session State
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "G.ONE"
        st.session_state.user_icon = archetypes["G.ONE"]["icon"]
        st.session_state.theme_color = archetypes["G.ONE"]["color"]

    # --- 2. CSS: RA.ONE THEME ---
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');

        /* --- GLOBAL SETTINGS --- */
        .stApp {{
            background-color: #030712;
            background-image: 
                linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            font-family: 'Rajdhani', sans-serif;
            overflow: hidden; 
        }}
        
        /* --- TEXT STYLES --- */
        h1, h2, h3 {{ font-family: 'Orbitron', sans-serif !important; letter-spacing: 1px; color: white; }}
        p, div, label {{ font-family: 'Rajdhani', sans-serif; color: #e0e7ff; }}

        /* --- INFO BOXES --- */
        .info-panel {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid {st.session_state.theme_color}40;
            border-left: 3px solid {st.session_state.theme_color};
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}

        /* --- THE BIG ICON (AVATAR) --- */
        .big-icon {{
            font-size: 80px;
            text-align: center;
            display: block;
            margin: 0 auto;
            filter: drop-shadow(0 0 15px {st.session_state.theme_color});
            animation: float 3s ease-in-out infinite;
        }}
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
            100% {{ transform: translateY(0px); }}
        }}

        /* --- BUTTONS --- */
        .stButton > button {{
            border: 1px solid {st.session_state.theme_color};
            color: {st.session_state.theme_color};
            background: transparent;
            font-family: 'Orbitron';
            height: 40px;
            width: 100%;
            transition: 0.3s;
        }}
        .stButton > button:hover {{
            background: {st.session_state.theme_color};
            color: #000;
        }}

        /* --- INPUT FIELDS --- */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: rgba(0,0,0,0.5) !important;
            border: 1px solid #475569 !important;
            color: white !important;
        }}
        
        /* Layout Tweaks */
        .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
        div[data-testid="stVerticalBlock"] > div {{ gap: 0.8rem !important; }}
        </style>
    """, unsafe_allow_html=True)

    # --- 3. NAVIGATION (BACK BUTTON) ---
    # Create a small column for the button so it doesn't span the whole width
    nav_col, spacer = st.columns([1, 8])
    with nav_col:
        if st.button("⬅ HOME"):
            # IMPORTANT: Replace 'current_page' with whatever variable name 
            # you use in your main app to control navigation!
            st.session_state.current_page = "home"  
            st.rerun()

    # --- 4. WELCOME HEADER ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"<h2>🚀 SET UP YOUR PROFILE</h2>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#94a3b8;'>Welcome! Customize your experience based on your tech skills.</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align:right; border:1px solid {st.session_state.theme_color}; padding:5px; color:{st.session_state.theme_color}; border-radius:5px; font-family:Orbitron; margin-top: 10px;'>STATUS: NEW USER</div>", unsafe_allow_html=True)

    st.divider()

    # --- 5. MAIN FORM LAYOUT ---
    col1, col2, col3 = st.columns([1, 0.8, 1.2], gap="medium")

    # === COL 1: CHOOSE PERSONA ===
    with col1:
        st.markdown(f"**1. What is your coding style?**")
        
        for name, data in archetypes.items():
            btn_label = f"{data['icon']} {name}"
            
            if st.button(btn_label, key=name, use_container_width=True):
                st.session_state.user_role = name
                st.session_state.user_icon = data["icon"]
                st.session_state.theme_color = data["color"]
                st.rerun()

        # Description Box
        current_data = archetypes[st.session_state.user_role]
        st.markdown(f"""
            <div class="info-panel" style="margin-top:10px;">
                <b style="color:{st.session_state.theme_color}">{current_data['role']}</b><br>
                <i style="font-size:14px;">"{current_data['desc']}"</i>
            </div>
        """, unsafe_allow_html=True)

    # === COL 2: VISUALIZE AVATAR ===
    with col2:
        st.markdown(f"<div style='text-align:center;'><b>2. Your Avatar</b></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        use_photo = st.toggle("Upload my own photo", value=False)
        st.markdown("<br>", unsafe_allow_html=True)

        if use_photo:
            uploaded_img = st.file_uploader("", type=['jpg', 'png'], label_visibility="collapsed")
            if uploaded_img:
                st.image(uploaded_img, width=150)
            else:
                st.info("Upload an image to see preview")
        else:
            st.markdown(f'<div class="big-icon">{st.session_state.user_icon}</div>', unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='text-align:center; color:{st.session_state.theme_color}; margin-top:10px;'>{st.session_state.user_role}</h3>", unsafe_allow_html=True)


    # === COL 3: ENTER DETAILS ===
    with col3:
        st.markdown(f"**3. Enter your Details**")
        
        with st.container():
            name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
            
            c_a, c_b = st.columns(2)
            with c_a: city = st.text_input("City / Location", placeholder="e.g. Mumbai")
            with c_b: college = st.text_input("College / University", placeholder="e.g. IIT Bombay")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**4. Upload Resume** <span style='font-size:12px; color:#64748b'>(Required for AI Analysis)</span>", unsafe_allow_html=True)
            
            resume = st.file_uploader("", type=['pdf', 'docx'], label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✨ CREATE MY PROFILE"):
                if not name or not resume:
                    st.error("Please enter your Name and Upload a Resume to proceed.")
                else:
                    st.toast("Profile Created Successfully!", icon="🎉")
                    time.sleep(1)
                    st.success(f"Welcome, {name}! Your {st.session_state.user_role} dashboard is ready.")

if __name__ == "__main__":
    show_profile_page()