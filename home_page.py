import streamlit as st
import importlib
import db_handler

# --- ICONS ---
SVG_ICONS = {
    "home": '<svg viewBox="0 0 24 24" width="20" height="20" stroke="#94a3b8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
    "profile": '<svg viewBox="0 0 24 24" width="20" height="20" stroke="#94a3b8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
    "bell": '<svg viewBox="0 0 24 24" width="20" height="20" stroke="#94a3b8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
    "shield": '<svg viewBox="0 0 24 24" width="20" height="20" stroke="#94a3b8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
    "logout": '<svg viewBox="0 0 24 24" width="20" height="20" stroke="#94a3b8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>',
    "salary": '<svg viewBox="0 0 24 24" width="32" height="32" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
    "aptitude": '<svg viewBox="0 0 24 24" width="32" height="32" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    "study": '<svg viewBox="0 0 24 24" width="32" height="32" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>',
}

# --- BACKGROUND IMAGES ---
BG_IMAGES = {
    "salary": "https://images.unsplash.com/photo-1592496001020-d31bd830651f?q=80&w=800&auto=format&fit=crop", 
    "hiring": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=800&auto=format&fit=crop", 
    "study": "https://images.unsplash.com/photo-1516110833967-0b5716ca1387?q=80&w=800&auto=format&fit=crop"
}

# --- HTML GENERATOR ---
def create_card_html(bg_url, icon_svg, title, label, desc, color_class):
    return (
        f'<div class="company-card {color_class}">'
        f'  <div class="watermark-bg" style="background-image: url(\'{bg_url}\');"></div>'
        f'  <div class="card-content-wrapper">'
        f'      <div class="card-logo-wrapper">'
        f'          {icon_svg}' 
        f'      </div>'
        f'      <div class="card-role-label">{label}</div>'
        f'      <div class="card-title">{title}</div>'
        f'      <div class="card-overview">{desc}</div>'
        f'  </div>'
        f'</div>'
    )

# --- CSS STYLING ---
def apply_dashboard_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
--bg-panel: rgba(10, 15, 30, 0.75);
--border-color: rgba(255, 255, 255, 0.1);
--green-primary: #10B981;
--blue-primary: #3B82F6;
--gold-primary: #F59E0B;
--text-main: #f8fafc;
--text-muted: #94a3b8;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
    background-color: #020617;
    
    /* 1. The Grid Lines (Linear Gradients) */
    /* 2. The Color Glows (Radial Gradients) */
    background-image: 
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 2px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);

    /* Define sizes: 50px square for grid, full screen for glows */
    background-size: 50px 50px, 50px 50px, 100% 100%, 100% 100%, 100% 100%;
    
    background-attachment: fixed;
}

.block-container { padding: 0 !important; max-width: 100% !important; }

@media (min-width: 992px) {
div[data-testid="column"]:nth-of-type(1) {
width: 280px !important; background: var(--bg-panel) !important;
border-right: 1px solid var(--border-color); backdrop-filter: blur(12px);
position: fixed !important; left: 0; top: 0; bottom: 0;
padding: 2rem 1.5rem !important; z-index: 100; box-shadow: 5px 0 20px rgba(0,0,0,0.2);
}
div[data-testid="column"]:nth-of-type(3) {
width: 320px !important; background: var(--bg-panel) !important;
border-left: 1px solid var(--border-color); backdrop-filter: blur(12px);
position: fixed !important; right: 0; top: 0; bottom: 0;
padding: 2rem 1.5rem !important; z-index: 100; box-shadow: -5px 0 20px rgba(0,0,0,0.2);
}
div[data-testid="column"]:nth-of-type(2) {
margin-left: 280px; margin-right: 320px; padding: 0 !important; 
background: transparent !important; height: 100vh; overflow-y: auto;
}
div[data-testid="column"]:nth-of-type(2)::-webkit-scrollbar { width: 0; background: transparent; }
}
@media (max-width: 991px) {
div[data-testid="column"] { width: 100% !important; padding: 20px !important; }
}

/* --- CARDS --- */
.company-card {
background: linear-gradient(145deg, rgba(30, 41, 59, 0.4), rgba(2, 6, 23, 0.6));
border: 1px solid var(--border-color); border-radius: 16px; padding: 30px 25px;
display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
height: 380px; position: relative; overflow: hidden; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
backdrop-filter: blur(5px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); z-index: 1; margin-bottom: 20px;
}
.company-card:hover { transform: translateY(-8px); }
.watermark-bg {
position: absolute; top: 0; left: 0; width: 100%; height: 100%;
background-repeat: no-repeat; background-position: center; background-size: cover;
opacity: 0.15; z-index: 0; pointer-events: none; filter: brightness(0.8) contrast(1.2);
}
.card-content-wrapper { position: relative; z-index: 2; width: 100%; display: flex; flex-direction: column; align-items: center; }
.card-logo-wrapper {
width: 80px; height: 80px; backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.03);
border-radius: 16px; display: flex; align-items: center; justify-content: center;
margin-bottom: 20px; padding: 12px; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
.company-card:hover .card-logo-wrapper { transform: scale(1.05); }
.card-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 8px; color: var(--text-main); text-align: center; }
.card-role-label {
font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 700;
padding: 6px 12px; border-radius: 30px; margin-bottom: 15px; text-align: center;
}
.card-overview { font-size: 0.95rem; color: var(--text-muted); text-align: center; margin-bottom: 15px; }

.card-green:hover { border-color: var(--green-primary); box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
.card-green .card-role-label { color: var(--green-primary); background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); }

.card-blue:hover { border-color: var(--blue-primary); box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
.card-blue .card-role-label { color: var(--blue-primary); background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); }

.card-gold:hover { border-color: var(--gold-primary); box-shadow: 0 0 20px rgba(245, 158, 11, 0.3); }
.card-gold .card-role-label { color: var(--gold-primary); background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); }

.explore-btn-container { margin-top: -55px; position: relative; z-index: 10; padding: 0 40px; }
div[data-testid="stButton"] button {
border: 1px solid var(--border-color); background: rgba(15, 23, 42, 0.8); color: var(--text-muted);
font-weight: 600; letter-spacing: 1px; backdrop-filter: blur(5px);
}
div[data-testid="stButton"] button:hover {
border-color: white !important; color: white !important; background: rgba(255, 255, 255, 0.1) !important;
}
.hero-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 15px; color:white; }
.hero-subtitle { font-size: 1.2rem; color: var(--text-muted); }
.icon-box { display: flex; align-items: center; justify-content: center; height: 35px; width: 24px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
def sidebar_menu_item(label, svg_key, page_name):
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        st.markdown(f'<div class="icon-box">{SVG_ICONS[svg_key]}</div>', unsafe_allow_html=True)
    with c2:
        if st.button(label, key=f"nav_{svg_key}"):
            st.session_state.current_page = page_name
            st.rerun()

# --- HOME PAGE CONTENT ---
def show_home():
    apply_dashboard_styles() 
    
    col_left, col_center, col_right = st.columns([1.8, 5, 2.2])

    # --- 1. LEFT SIDEBAR ---
    with col_left:
        st.markdown("""
<div style="margin-bottom: 40px; padding-top: 20px;">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="width: 42px; height: 42px; background: linear-gradient(135deg, #3b82f6, #10b981); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 24px; color: white; box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);">B</div>
<div>
<div style="font-size: 20px; font-weight: 800; color: white; line-height: 1; letter-spacing: -0.5px;">BCASprint</div>
<div style="font-size: 10px; font-weight: 700; color: #94a3b8; letter-spacing: 2px; margin-top: 6px;">CAREER ENGINE</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

        # ----------------------------------------------------
        # DYNAMIC USER INFO (Fixes the "New user as Admin" bug)
        # ----------------------------------------------------
        user_info = st.session_state.get('user_info', {})
        current_username = user_info.get('username', 'Guest')
        # Ensure role is lowercase for comparison, fallback to 'user'
        current_role = user_info.get('role', 'user').lower()
        
        # Determine badge color based on role
        if current_role in ['admin', 'super_admin']:
            role_color = "#10b981" # Green
            role_text = "ADMIN ACCESS"
        else:
            role_color = "#3b82f6" # Blue
            role_text = "STUDENT"

        st.markdown(f"""
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 16px; margin-bottom: 40px; backdrop-filter: blur(5px);">
<div style="font-size: 10px; color: #64748b; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Logged in as</div>
<div style="font-size: 16px; font-weight: 700; color: white; margin-bottom: 4px;">{current_username}</div>
<div style="font-size: 9px; font-weight: 800; color: {role_color}; display: inline-block; background: rgba(16, 185, 129, 0.1); padding: 4px 10px; border-radius: 20px; border: 1px solid {role_color}; letter-spacing: 1px;">{role_text}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div style="color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 20px; padding-left: 5px;">MAIN MENU</div>', unsafe_allow_html=True)
        sidebar_menu_item("Home", "home", "Home")
        sidebar_menu_item("Profile", "profile", "Profile")
        sidebar_menu_item("Notifications", "bell", "Notifications")

        # ----------------------------------------------------
        # CONDITIONAL ADMIN PANEL (Fixes visibility issue)
        # ----------------------------------------------------
        if current_role in ['admin', 'super_admin']:
            st.markdown('<div style="color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-top: 40px; margin-bottom: 20px; padding-left: 5px;">ADMIN TOOLS</div>', unsafe_allow_html=True)
            sidebar_menu_item("Admin Panel", "shield", "Admin")

        c1, c2 = st.columns([0.15, 0.85])
        with c1:
            st.markdown(f'<div class="icon-box" style="margin-top: -5px;">{SVG_ICONS["logout"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="logout-box">', unsafe_allow_html=True)
            if st.button("Logout", key="nav_logout"):
                st.session_state.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- 2. CENTER CONTENT ---
    with col_center:
        st.markdown(f"""
<div style="text-align: center; padding: 50px 20px; margin-bottom: 30px;">
<div class="hero-title">Welcome, {current_username.split()[0]}!</div>
<div class="hero-subtitle">Your professional command center for recruitment analytics, salary prediction engines, and curated career resources.</div>
</div>
""", unsafe_allow_html=True)

        # MODULE CARDS
        c1, c2, c3 = st.columns(3)
        cards = [
            {
                "title": "Salary Predictor", 
                "label": "AI ENGINE",
                "desc": "Leverage machine learning to forecast potential compensation based on skills and market data.", 
                "icon": SVG_ICONS['salary'], 
                "bg_image": BG_IMAGES['salary'], 
                "page": "Salary", 
                "btn_key": "btn_salary",
                "color_class": "card-green" # GREEN
            },
            {
                "title": "Hiring Intelligence", 
                "label": "LIVE DATA",
                "desc": "Real-time analytics on active hiring drives and aptitude test requirements.", 
                "icon": SVG_ICONS['aptitude'], 
                "bg_image": BG_IMAGES['hiring'], 
                "page": "Hiring", 
                "btn_key": "btn_hiring",
                "color_class": "card-blue" # BLUE
            },
            {
                "title": "Study Resources", 
                "label": "CURATED PATHS",
                "desc": "Structured technical roadmaps and essential learning materials for BCA professionals.", 
                "icon": SVG_ICONS['study'], 
                "bg_image": BG_IMAGES['study'], 
                "page": "Study", 
                "btn_key": "btn_study",
                "color_class": "card-gold" # GOLD
            }
        ]

        for i, col in enumerate([c1, c2, c3]):
            card = cards[i]
            with col:
                html_code = create_card_html(card['bg_image'], card['icon'], card['title'], card['label'], card['desc'], card['color_class'])
                st.markdown(html_code, unsafe_allow_html=True)
                
                st.markdown('<div class="explore-btn-container">', unsafe_allow_html=True)
                if st.button("LAUNCH MODULE", key=card['btn_key']):
                    st.session_state.current_page = card['page']
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. RIGHT SIDEBAR (REAL DB DATA) ---
    with col_right:
        st.markdown("""
            <div style="margin-top: 40px;"></div>
        """, unsafe_allow_html=True)

        # FETCH USER HISTORY FROM DATABASE
        # This returns a list of tuples: (DateStr, Role, PredictionDetails)
        user_history = db_handler.get_user_history(current_username)

        # 1. DYNAMIC "LATEST INSIGHT" CARD
        if user_history:
            # Get the most recent prediction (first item)
            last_date, last_role, last_val = user_history[0]
            
            st.markdown(f"""
<div style="font-size: 10px; font-weight: 800; letter-spacing: 1.5px; color: #8b5cf6; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
<span style="width: 6px; height: 6px; background: #8b5cf6; border-radius: 50%; display:inline-block;"></span> LATEST INSIGHT
</div>
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 30px; backdrop-filter: blur(5px);">
<div style="font-weight: 700; color: white; font-size: 15px; margin-bottom: 15px; letter-spacing: -0.5px;">{last_role}</div>
<div style="margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; margin-bottom: 6px; font-weight: 500;">
<span>Prediction Date</span>
<span style="color: white; font-weight: 600;">{last_date}</span>
</div>
</div>
<div style="width: 100%; height: 1px; background: linear-gradient(90deg, #1e293b, transparent); margin: 15px 0;"></div>
<div style="display: flex; justify-content: space-between; font-size: 13px; align-items: center;">
<span style="color: #94a3b8; font-weight: 500;">Est. Salary</span>
<span style="color: #8b5cf6; font-weight: 800; font-size: 15px;">{last_val.split('(')[0]}</span>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            # Placeholder if no data exists
            st.markdown("""
<div style="font-size: 10px; font-weight: 800; letter-spacing: 1.5px; color: #8b5cf6; margin-bottom: 15px;">
LATEST INSIGHT
</div>
<div style="border: 1px dashed #334155; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px;">
<p style="font-size: 12px; color: #64748b;">No predictions yet.</p>
<p style="font-size: 11px; color: #475569;">Use the Salary Predictor to generate insights.</p>
</div>
""", unsafe_allow_html=True)

        # 2. DYNAMIC "RECENT ACTIVITY" LIST
        st.markdown("""
<div style="font-size: 10px; font-weight: 800; letter-spacing: 1.5px; color: #10b981; margin-bottom: 15px; margin-top: 40px; display: flex; align-items: center; gap: 8px;">
<span style="width: 6px; height: 6px; background: #10b981; border-radius: 50%; display:inline-block;"></span> RECENT ACTIVITY
</div>
""", unsafe_allow_html=True)

        if user_history:
            for date, role, details in user_history:
                st.markdown(f"""
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; transition: all 0.2s ease; cursor: default;" onmouseover="this.style.borderColor='#10b981';this.style.background='rgba(16, 185, 129, 0.05)';" onmouseout="this.style.borderColor='rgba(16, 185, 129, 0.3)';this.style.background='rgba(255,255,255,0.02)';">
<div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
<span style="color: white; font-weight: 600;">{role}</span>
<span style="color: #64748b; font-weight: 500;">{date}</span>
</div>
<div style="font-size: 10px; color: #94a3b8;">{details}</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size: 12px; color: #64748b; font-style: italic;">No activity history found.</div>', unsafe_allow_html=True)