import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Try importing the database handler
try:
    import db_handler
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ==========================================
# 1. DATA CONTROLLER (OPTIMIZED WITH CACHING)
# ==========================================

# 1. Cache the DB Availability Check (Runs once)
@st.cache_resource
def check_db_connection():
    """Checks if we can actually connect to the DB."""
    if DB_AVAILABLE:
        conn = db_handler.get_connection()
        if conn:
            conn.close()
            return True
    return False

USE_REAL_DB = check_db_connection()

# 2. Cache KPI Data (Refreshes every 60 seconds)
@st.cache_data(ttl=60)
def get_kpi_data_hybrid():
    """Fetches real stats if DB is live, else mock."""
    if USE_REAL_DB:
        try:
            real_stats = db_handler.get_dashboard_kpis() 
            return {
                "total_users": real_stats.get('users', 0),
                "total_admins": real_stats.get('admins', 0),
                "predictions_24h": real_stats.get('predictions', 0), 
                "pending_feedback": 0 
            }
        except Exception as e:
            print(f"KPI Fetch Error: {e}")
    return get_kpi_mock()

# 3. Cache User List (Refreshes every 60 seconds)
@st.cache_data(ttl=60)
def get_users_hybrid():
    """Fetches real users if DB is live, else mock."""
    if USE_REAL_DB:
        try:
            raw_users = db_handler.get_all_users()
            formatted_users = []
            for u in raw_users:
                role_display = "Admin" if u['role'] in ['admin', 'super_admin'] else "User"
                joined_date = str(u['Joined']) if u['Joined'] else "-"
                formatted_users.append({
                    "ID": f"DB-{u['id']}",
                    "Name": u['username'],
                    "Email": u['email'],
                    "Role": role_display, 
                    "Joined": joined_date,
                    "Last Login": u.get('Last Login', '-')
                })
            return formatted_users
        except Exception as e:
            print(f"User Fetch Error: {e}")
            
    # Return Mock if DB not connected
    return init_mock_data()

# 4. Cache Logs (Refreshes every 30 seconds)
@st.cache_data(ttl=30)
def get_logs_hybrid():
    """Fetches real logs if DB is live, else mock."""
    if USE_REAL_DB:
        try:
            raw_logs = db_handler.get_recent_logs(limit=50)
            if raw_logs:
                return pd.DataFrame(raw_logs)
        except Exception:
            pass
    return get_real_login_table_mock()

# ==========================================
# 2. MOCK DATA GENERATORS (Cached for Speed)
# ==========================================

@st.cache_data
def init_mock_data():
    users = []
    for i in range(101, 106):
        users.append({
            "ID": f"USR-{i}", "Name": f"Student {i}",
            "Email": f"student{i}@bcasprint.com", "Role": "User", "Joined": "2024-11-15"
        })
    users.append({
        "ID": "ADM-001", "Name": "Chetana Garud", "Email": "admin@bcasprint.com", "Role": "Admin", "Joined": "2023-01-01"
    })
    return users

@st.cache_data
def get_kpi_mock():
    return {"total_users": 105, "total_admins": 1, "predictions_24h": 342, "pending_feedback": 12}

@st.cache_data
def get_user_growth_data():
    dates = pd.date_range(start="2025-01-01", periods=30)
    users = np.cumsum(np.random.randint(5, 20, 30))
    return pd.DataFrame({"Date": dates, "New Users": users})

@st.cache_data
def get_predictions_by_role_data():
    roles = ['Data Scientist', 'Web Developer', 'System Analyst', 'Software Engineer', 'AI Specialist']
    counts = [450, 300, 150, 500, 200]
    return pd.DataFrame({"Role": roles, "Count": counts})

@st.cache_data
def get_user_login_stats():
    data = []
    for _ in range(50): 
        role = np.random.choice(['Student', 'Admin', 'Guest', 'Mentor'], p=[0.6, 0.1, 0.2, 0.1])
        login_count = np.random.randint(5, 100) if role == 'Student' else np.random.randint(50, 150)
        data.append({"Role": role, "Total Logins": login_count})
    return pd.DataFrame(data)

@st.cache_data
def get_real_login_table_mock():
    data = []
    users = init_mock_data()
    for user in users:
        login_count = np.random.randint(0, 55)
        status = "Active" if login_count > 10 else "Inactive"
        data.append({
            "User Name": user['Name'], "Role": user.get('Role', 'User'),
            "Total Logins": login_count,
            "Last Login": (datetime.now() - timedelta(hours=np.random.randint(1, 72))).strftime("%Y-%m-%d %H:%M"),
            "Status": status
        })
    return pd.DataFrame(data).sort_values(by="Total Logins", ascending=False)

@st.cache_data
def get_module_usage_data():
    return pd.DataFrame({"Module": ['AI Predictor', 'Study Material', 'Job Board', 'Profile'], "Active Users": [120, 85, 45, 30]})

@st.cache_data
def get_hiring_notifications():
    jobs = ["Jr. Python Dev", "Data Analyst Intern", "React Frontend Dev"]
    data = [{"Date Sent": datetime.now().strftime("%Y-%m-%d"), "Job Title": np.random.choice(jobs), "Status": "Sent"} for _ in range(5)]
    return pd.DataFrame(data)

# ==========================================
# 3. UI ASSETS & HELPERS
# ==========================================
def get_svg(icon_name, width=24, height=24, color="#00E5FF"):
    """Neon outlined icons."""
    icons = {
        "shield": f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 5px {color});"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>""",
        "lightning": f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 5px {color});"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>""",
        "user_plus": f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 5px {color});"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>""",
        "user_minus": f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="#FF0055" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 5px #FF0055);"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="23" y1="11" x2="17" y2="11"></line></svg>""",
        "dashboard": f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 0px 5px {color});"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>"""
    }
    return icons.get(icon_name, "")

def render_header(icon, text):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 35px; border-bottom: 2px solid #1F1B2E; padding-bottom: 20px;">
        <div style="background: rgba(0, 229, 255, 0.1); padding: 12px; border-radius: 12px; border: 1px solid #00E5FF; box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);">
            {get_svg(icon, 32, 32, '#00E5FF')}
        </div>
        <h1 style="margin: 0; padding: 0; font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 3rem; color: white; text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); text-transform: uppercase; letter-spacing: 2px;">{text}</h1>
    </div>
    """, unsafe_allow_html=True)

def local_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;600&display=swap');
        
        .stApp { background: radial-gradient(circle at top left, #141021, #090510); }
        h1, h2, h3, h4 { font-family: 'Rajdhani', sans-serif !important; letter-spacing: 1px; color: #fff; }
        p, div, span, label { font-family: 'Inter', sans-serif; color: #A0A0C0; }

        /* METRIC CARDS */
        [data-testid="stMetric"] { background: rgba(25, 22, 39, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00E5FF; border-radius: 4px; padding: 20px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3); backdrop-filter: blur(5px); transition: all 0.3s ease; }
        [data-testid="stMetric"]:hover { border-left-color: #FF00E6; transform: translateX(5px); box-shadow: 0 0 20px rgba(255, 0, 230, 0.1); }
        [data-testid="stMetricLabel"] { color: #8F8FA8 !important; font-size: 14px !important; text-transform: uppercase; letter-spacing: 1px; }
        [data-testid="stMetricValue"] { color: #fff !important; font-family: 'Rajdhani'; font-weight: 700; font-size: 36px !important; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }

        /* INPUT FIELDS */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div { background-color: #0F0B18 !important; color: #00E5FF !important; border: 1px solid #2D2D45 !important; border-radius: 0px !important; font-family: 'Rajdhani'; }
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within { border-color: #00E5FF !important; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important; }

        /* BUTTONS */
        div.stButton > button { background: transparent; color: #00E5FF !important; border: 1px solid #00E5FF; border-radius: 0px; padding: 0.6rem 1.5rem; font-family: 'Rajdhani'; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s; }
        div.stButton > button:hover { background: #00E5FF; color: #000 !important; box-shadow: 0 0 20px #00E5FF; }
        div.stButton > button:first-child { border-color: #555; color: #aaa !important; }
        div.stButton > button:first-child:hover { border-color: #fff; color: #fff !important; box-shadow: 0 0 10px white; }

        /* TABLES */
        [data-testid="stDataFrame"] { border: 1px solid #2D2D45; background-color: #0F0B18; }
        
        /* ADMIN ZONE */
        .admin-zone { background: linear-gradient(180deg, rgba(255, 0, 85, 0.05), rgba(0,0,0,0)); border: 1px solid #FF0055; border-radius: 4px; padding: 30px; box-shadow: 0 0 30px rgba(255, 0, 85, 0.1); position: relative; }
        .admin-zone::before { content: "SECURE AREA"; position: absolute; top: -10px; right: 20px; background: #090510; color: #FF0055; padding: 0 10px; font-family: 'Rajdhani'; font-weight: bold; font-size: 12px; letter-spacing: 2px; }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #2D2D45; }
        .stTabs [data-baseweb="tab"] { background: transparent; color: #555; font-family: 'Rajdhani'; letter-spacing: 1px; }
        .stTabs [aria-selected="true"] { color: #00E5FF !important; border-bottom: 2px solid #00E5FF !important; text-shadow: 0 0 8px rgba(0, 229, 255, 0.6); }
        </style>
    """, unsafe_allow_html=True)

def setup_dark_plots():
    plt.style.use('dark_background')
    sns.set_theme(style="dark", rc={
        "axes.facecolor": "#090510", "figure.facecolor": "#090510", "grid.color": "#1F1B2E",
        "text.color": "#A0A0C0", "xtick.color": "#5E5E75", "ytick.color": "#5E5E75",
        "axes.labelcolor": "#A0A0C0", "axes.edgecolor": "#090510", "font.family": "monospace"
    })

# ==========================================
# 4. MAIN PAGE LOGIC
# ==========================================
def show_admin_page():
    local_css()
    setup_dark_plots() 

    # --- HYBRID DATA LOADING ---
    user_db = get_users_hybrid()
    kpi = get_kpi_data_hybrid()
    
    # --- HEADER ---
    c_head, c_role = st.columns([3, 1])
    with c_head: render_header("dashboard", "SYSTEM DASHBOARD")
    with c_role:
        st.markdown('<div style="text-align:right; margin-top:10px;">', unsafe_allow_html=True)
        
        # Use session state role if available, otherwise default to Admin for view
        current_role = st.session_state.get('user_info', {}).get('role', 'admin')
        role_label = "SUPER ADMIN" if current_role == 'super_admin' else "ADMIN"
        
        st.markdown(f'<span style="color:#00E5FF; font-family:Rajdhani; font-size:1.2rem; font-weight:bold;">{role_label}</span>', unsafe_allow_html=True)
        
        if USE_REAL_DB:
            st.markdown('<span style="color:#39FF14; font-size:12px;">● LIVE DB CONNECTED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#FFEA00; font-size:12px;">● RUNNING IN SIMULATION MODE</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("<< RETURN TO BASE"):
        st.session_state.current_page = "Home"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- METRICS HUD ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ACTIVE UNITS", kpi['total_users'], "SYNCED")
    c2.metric("CONTROLLERS", kpi['total_admins'], "SECURE")
    c3.metric("AI QUERIES", kpi['predictions_24h'], "HIGH LOAD")
    c4.metric("PENDING FB", kpi['pending_feedback'], "WAITING") 

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- VISUALIZATION (Uses Simulated Data for complex charts to keep UI intact) ---
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("### 📈 NETWORK TRAFFIC")
        growth_data = get_user_growth_data()
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=growth_data, x="Date", y="New Users", color="#00E5FF", linewidth=2, ax=ax1)
        ax1.fill_between(growth_data["Date"], growth_data["New Users"], color="#00E5FF", alpha=0.05)
        sns.scatterplot(data=growth_data[::4], x="Date", y="New Users", color="#fff", s=30, ax=ax1, edgecolor="#00E5FF", linewidth=2)
        ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False); ax1.spines['left'].set_visible(False)
        ax1.grid(True, linestyle='--', alpha=0.2, color="#00E5FF")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    with col_b:
        st.markdown("### 🧩 ROLE DISTRIBUTION")
        role_data = get_predictions_by_role_data()
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        colors = ["#00E5FF", "#FF00E6", "#39FF14", "#FFEA00", "#7C4DFF"]
        ax2.pie(role_data["Count"], labels=role_data["Role"], colors=colors, autopct='%1.1f%%', pctdistance=0.85, startangle=140, textprops={'color': "#fff", 'fontsize': 10, 'fontfamily': 'monospace'}, wedgeprops={'edgecolor': '#090510', 'linewidth': 3})
        fig2.gca().add_artist(plt.Circle((0,0), 0.70, fc='#090510', ec='#2D2D45', linewidth=1))
        st.pyplot(fig2)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 2 ---
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("### 🧬 USER DENSITY")
        st.caption("Login Frequency Heatmap")
        login_stats_mock = get_user_login_stats()
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.violinplot(x="Role", y="Total Logins", hue="Role", legend=False, data=login_stats_mock, palette="plasma", inner="quart", ax=ax3, linewidth=1)
        ax3.spines['top'].set_visible(False); ax3.spines['right'].set_visible(False); ax3.spines['left'].set_visible(False)
        st.pyplot(fig3)

    with col_d:
        st.markdown("### ⚡ MODULE LOAD")
        st.caption("System Resource Allocation")
        module_data = get_module_usage_data()
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Active Users", y="Module", data=module_data, color="#39FF14", ax=ax4, edgecolor=None, alpha=0.8)
        for container in ax4.containers: ax4.bar_label(container, color='#fff', padding=5, fontsize=10, fontfamily='monospace')
        ax4.spines['top'].set_visible(False); ax4.spines['right'].set_visible(False); ax4.spines['left'].set_visible(False); ax4.spines['bottom'].set_visible(False)
        ax4.set_xticks([]) 
        st.pyplot(fig4)

    # --- LOGS ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 💾 SYSTEM LOGS")
    t1, t2 = st.tabs(["ACCESS LOGS", "TRANSMISSIONS"])
    with t1: st.dataframe(get_logs_hybrid(), width=1000)
    with t2: st.dataframe(get_hiring_notifications(), width=1000)

    # --- SUPER ADMIN ZONE ---
    # Only show if role is strictly super_admin
    if current_role == "super_admin":
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="admin-zone">', unsafe_allow_html=True)
            render_header("lightning", "SUPERUSER PROTOCOLS")
            
            c_add, c_remove = st.columns(2)
            
            # --- ADD USER ---
            with c_add:
                st.markdown(f"""<div style="display:flex; align-items:center; gap:8px; color:#00E5FF; margin-bottom:15px; font-family:'Rajdhani'; font-size:1.2rem;">
                                {get_svg('user_plus', 20, 20, '#00E5FF')} <b>INJECT NEW NODE</b></div>""", unsafe_allow_html=True)
                with st.form("add_user_form", clear_on_submit=True):
                    new_name = st.text_input("NODE IDENTIFIER (Name)")
                    new_email = st.text_input("COMM LINK (Email)")
                    new_password = st.text_input("KEY (Password)", type="password")
                    new_role_ui = st.selectbox("PERMISSION LEVEL", ["User", "Admin"])
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button(">> EXECUTE INJECTION"):
                        if new_name and new_email and new_password:
                            # REAL DB LOGIC
                            if USE_REAL_DB:
                                db_role = "admin" if new_role_ui == "Admin" else "user"
                                success = db_handler.create_user(new_name, new_email, new_password, db_role, 1)
                                if success:
                                    st.success(f"NODE INJECTED INTO DATABASE: {new_name}")
                                    st.rerun()
                                else:
                                    st.error("INJECTION FAILED (Check DB logs or duplicates)")
                            # MOCK LOGIC
                            else:
                                prefix = "ADM" if new_role_ui == "Admin" else "USR"
                                new_id = f"{prefix}-{len(st.session_state['user_db']) + 101}"
                                st.session_state['user_db'].append({"ID": new_id, "Name": new_name, "Email": new_email, "Role": new_role_ui, "Joined": datetime.now().strftime("%Y-%m-%d")})
                                st.success(f"SIMULATION NODE CREATED: {new_name}")
                                st.rerun()
                        else: st.warning("ALL FIELDS REQUIRED")

            # --- DELETE USER ---
            with c_remove:
                st.markdown(f"""<div style="display:flex; align-items:center; gap:8px; color:#FF0055; margin-bottom:15px; font-family:'Rajdhani'; font-size:1.2rem;">
                                {get_svg('user_minus', 20, 20, '#FF0055')} <b>PURGE NODE</b></div>""", unsafe_allow_html=True)
                
                # Filter Super Admin from deletion list visually
                safe_users = [u for u in user_db if u['Name'] != "Chetana Garud"]
                
                target_group = st.radio("TARGET CLUSTER:", ["Users", "Admins"], horizontal=True)
                filtered_list = [u for u in safe_users if u.get('Role') == ('User' if target_group == "Users" else 'Admin')]
                user_names = [u['Name'] for u in filtered_list]
                
                if not user_names: st.info("CLUSTER EMPTY")
                else: target_user = st.selectbox(f"SELECT TARGET", user_names)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(">> INITIALIZE PURGE"):
                    if 'target_user' in locals() and target_user:
                        # SUPER ADMIN PROTECTION
                        if target_user == "Chetana Garud":
                            st.error("⛔ ACCESS DENIED: CANNOT PURGE SUPER ADMIN")
                        else:
                            # REAL DB LOGIC
                            if USE_REAL_DB:
                                if db_handler.delete_user(target_user):
                                    st.error(f"NODE PURGED FROM DB: '{target_user}'")
                                    st.rerun()
                                else:
                                    st.warning("PURGE FAILED (DB Error or Restricted)")
                            # MOCK LOGIC
                            else:
                                st.session_state['user_db'] = [u for u in st.session_state['user_db'] if u['Name'] != target_user]
                                st.error(f"SIMULATION NODE PURGED: '{target_user}'")
                                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
            with st.expander(">> DECRYPT FULL DATABASE"):
                 st.dataframe(pd.DataFrame(user_db), width=1000)

    elif current_role == "admin":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(255, 234, 0, 0.05); padding: 15px; border: 1px solid #FFEA00; color: #FFEA00; font-family: 'Rajdhani'; letter-spacing: 1px;">
            ⚠️ <b>ACCESS DENIED:</b> ELEVATED PRIVILEGES REQUIRED FOR NODE MANAGEMENT.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_admin_page()