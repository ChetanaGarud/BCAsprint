# runner.py - SALARY PREDICTOR (Corrected User Logging)
import streamlit as st
import json
import pandas as pd
import joblib
import os 
import google.generativeai as genai
import plotly.graph_objects as go
import numpy as np 
import db_handler as db 
from typing import List, Dict, Optional, Tuple


# --- Configuration: File Paths ---
MODEL_FILE = "best_model4.PKL" 
TRAINING_CSV = "BCA_Salary_Dataset_50k_v3.csv"
RETRAIN_CSV = "retrain_records.csv"

# --- Feature Columns ---
FEATURE_INPUT_COLS = [
    "District", "Company_Type", "Job_Role_Level",
    "Internship_Exp", "CGPA", "College_Tier",
]
TARGET_COL = "Annual_Salary_Rupees"

# --- HELPER FUNCTIONS ---

@st.cache_resource 
def load_model(path=MODEL_FILE):
    """Loads the pre-trained salary prediction model."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_PATH = os.path.join(BASE_DIR, path)
    
    if not os.path.exists(FULL_PATH):
        st.warning(f"⚠️ Model file not found at '{FULL_PATH}'. Using a dummy model.")
        class DummyModel:
            def predict(self, df): return np.array([350000])
        return DummyModel()

    try:
        model = joblib.load(FULL_PATH) 
        if not hasattr(model, 'predict'):
            st.error("❌ Loaded object is not a valid model (missing 'predict' method).")
            return None
        return model
    except Exception as e:
        st.error(f"❌ **Error loading model:** {e}")
        return None

# --- Gemini API Functions and Fallbacks ---

FREE_RESOURCES = {
    "sql": "https://www.simplilearn.com/free-online-course-to-learn-sql-basics-skillup",
    "python": "https://www.analyticsvidhya.com/courses/introduction-to-data-science/",
    "dsa": "https://leetcode.com/", 
    "comm": "https://www.coursera.org/learn/effective-communication-skills",
    "cloud": "https://www.mygreatlearning.com/cloud-computing/free-courses",
    "itil": "https://skillsbuild.org/courses/itil-foundation-course",
    "security": "https://www.edx.org/course/introduction-to-cybersecurity",
    "tableau": "https://www.tableau.com/learn/training/free",
}

COMMON_RECS = {
    "comm_high": {"name":"Advanced Communication Skills", "reason":"Crucial for better offers and client interaction.", "link": FREE_RESOURCES['comm'], "priority":"High"},
    "sql_high": {"name":"SQL Mastery and Database Fundamentals", "reason":"Essential foundation for all data and backend roles.", "link": FREE_RESOURCES['sql'], "priority":"High"},
    "python_data_high": {"name":"Python for Data Analysis (Pandas, NumPy)", "reason":"Necessary for data manipulation and scripting automation.", "link": FREE_RESOURCES['python'], "priority":"High"},
    "dsa_high": {"name":"Data Structures & Algorithms Practice", "reason":"Core skill required for all major tech company interviews.", "link": FREE_RESOURCES['dsa'], "priority":"High"},
    "cloud_med": {"name":"Cloud Computing Fundamentals (AWS/Azure)", "reason":"Highly demanded skill in modern infrastructure.", "link": FREE_RESOURCES['cloud'], "priority":"Medium"},
    "itil_med": {"name":"ITIL Foundation Certification Prep", "reason":"Standardize IT service management best practices.", "link": FREE_RESOURCES['itil'], "priority":"Medium"},
    "sec_high": {"name":"Cybersecurity Basics and Network Defense", "reason":"Foundation for security and critical infrastructure roles.", "link": FREE_RESOURCES['security'], "priority":"High"},
    "viz_med": {"name":"Data Visualization (Tableau/Power BI Basics)", "reason":"Effective presentation of data insights to stakeholders.", "link": FREE_RESOURCES['tableau'], "priority":"Medium"},
}

def fallback_recs(role: str) -> List[Dict]:
    """Provides default recommendations if the AI recommender fails."""
    return [COMMON_RECS["dsa_high"], COMMON_RECS["sql_high"], COMMON_RECS["comm_high"], COMMON_RECS["cloud_med"]]

def build_gemini_prompt(salary_min: float, salary_max: float, role: str, district: Optional[str] = None) -> str:
    prompt = (
        f"You are a practical career advisor for BCA graduates in India. Your goal is to provide specific, job-role-based advice. "
        f"The candidate's predicted salary range is INR {int(salary_min):,} to {int(salary_max):,} for the role '{role}'. "
    )
    if district:
        prompt += f"Their target location is {district}, Maharashtra. "
    prompt += (
        "Provide a maximum of 4 concise, actionable recommendations (courses, certifications, or skills) "
        "that are MOST RELEVANT to the '{role}' position. "
        "For each recommendation, find the **BEST FREE website link (URL)** to start learning or obtaining the certification/course. "
        "Format the output STRICTLY as a JSON array of objects. Each object must have these keys: "
        "'name' (string, the recommendation title), "
        "'reason' (string, brief justification, max 15 words), "
        "'link' (string, the exact free course URL), " 
    )
    return prompt
    
def call_gemini(prompt: str, timeout: int = 25) -> Optional[str]:
    """Calls the Gemini API using the retrieved secret key."""
    api_key = None
    try:
        if 'gemini' in st.secrets and 'api_key' in st.secrets.gemini:
            api_key = st.secrets.gemini.api_key
        elif st.secrets.get("GEMINI_API_KEY"):
            api_key = st.secrets.get("GEMINI_API_KEY")
        else:
            api_key = os.environ.get("GEMINI_API_KEY") 
    except (AttributeError, KeyError):
        api_key = os.environ.get("GEMINI_API_KEY") 
        
    if not api_key: 
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash') 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: 
        print(f"Error calling google-generativeai: {e}")
        return None

def parse_json_array(text: str) -> Optional[List[Dict]]:
    if not text: return None
    try:
        start_index = text.find('[')
        end_index = text.rfind(']')
        if start_index != -1 and end_index != -1 and end_index >= start_index:
            json_str = text[start_index : end_index + 1]
            parsed = json.loads(json_str)
            if isinstance(parsed, list): return parsed
        parsed = json.loads(text)
        if isinstance(parsed, list): return parsed
        return None
    except Exception as e:
        print(f"JSON Decode Error: {e}")
        return None

# --- Load Training Data (Cached) ---
@st.cache_data 
def load_training_data(path=TRAINING_CSV):
    """Loads and cleans the model training data."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_PATH = os.path.join(BASE_DIR, path)

    if not os.path.exists(FULL_PATH): 
        st.warning(f"⚠️ Training data ('{path}') not found. Using dummy data.")
        dummy_data = {
            "District": ["Pune", "Thane", "Mumbai Suburban", "Other"], 
            "Company_Type": ["Service-Based MNC", "Startup", "Product-Based MNC", "Mid-Sized Indian Co."], 
            "Job_Role_Level": ["Software Developer - GET", "IT Support Specialist - SDA"], 
            "Internship_Exp": ["6-12 months", "None"], 
            "CGPA": ["8.0-8.9", "7.0-7.9"], 
            "College_Tier": ["Tier-2", "Tier-3"],
            TARGET_COL: [550000, 300000, 400000, 600000]
        }
        return pd.DataFrame(dummy_data)
        
    try:
        df = pd.read_csv(FULL_PATH)
        required = FEATURE_INPUT_COLS + [TARGET_COL]
        missing = [c for c in required if c not in df.columns]
        if missing: st.error(f"❌ Training data missing: {missing}"); return None
        df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors='coerce')
        df.dropna(subset=[TARGET_COL], inplace=True)
        return df
    except Exception as e: st.error(f"❌ Error loading training data: {e}"); return None
    
@st.cache_data 
def get_options(df, column, fallback):
    """Gets unique options for selectboxes from the training data."""
    if df is not None and column in df.columns:
        opts = sorted(df[column].dropna().unique().tolist())
        
        if column == "Internship_Exp":
            if "None" not in opts: opts.insert(0, "None")
            
        filtered_fallback = [item for item in fallback if item not in ["Other", "Other / Not Listed"]]
        
        final_opts = list(set(opts) | set(filtered_fallback))
        final_opts.sort()

        if "Not Listed" not in final_opts and column == "Job_Role_Level":
            final_opts.append("Not Listed")
            
        return final_opts if final_opts else fallback
    
    if column == "Internship_Exp" and "None" not in fallback: 
        fallback.insert(0, "None")
    
    return fallback

def pseudo_predict_with_gemini(input_row: Dict, custom_role: str) -> Optional[float]:
    """Uses Gemini to generate a pseudo-salary center point."""
    prompt = f"""
    You are an expert salary benchmarking AI. The candidate has the following profile details:
    - Target Role: {custom_role}
    - Location: {input_row.get('District', 'Maharashtra')}
    - Academic Level: {input_row.get('College_Tier', 'Tier-3')} college, CGPA {input_row.get('CGPA', '7.0-7.9')}
    - Internship Experience: {input_row.get('Internship_Exp', 'None')}
    - Targeting Company Type: {input_row.get('Company_Type', 'Service-Based MNC')}
    
    Estimate a realistic **CENTER ANNUAL SALARY (in INR)** for a fresh BCA graduate with this profile in India applying for the **{custom_role}** role. 
    Output ONLY the raw numerical value of the estimated salary (e.g., 650000) with no text, commas, or currency symbols.
    """
    
    response_text = call_gemini(prompt)
    
    if response_text:
        try:
            salary_estimate = float("".join(c for c in response_text if c.isdigit() or c == '.'))
            return max(200000.0, min(salary_estimate, 2000000.0))
        except ValueError:
            return None
    return None

def calculate_prediction_and_recs(input_row: Dict, is_custom_role: bool, model, train_df) -> Tuple[float, float, float, List[Dict]]:
    """Performs the main prediction and recommendation logic."""
    center_salary = None
    
    if is_custom_role:
        custom_role_name = input_row['Job_Role_Level']
        st.info(f"Generating salary estimate for custom role: **{custom_role_name}** using AI contextual analysis...")
        center_salary = pseudo_predict_with_gemini(input_row, custom_role_name)
        
        if center_salary is None:
            st.error("AI estimation failed. Using a base entry-level salary range.")
            center_salary = 300000.0 
        else:
            st.success("AI estimation complete!")

    else:
        input_df = pd.DataFrame([input_row], columns=FEATURE_INPUT_COLS)
        temp_input_df = input_df.copy()
        if temp_input_df.iloc[0]['Internship_Exp'] == 'None':
            temp_input_df.iloc[0]['Internship_Exp'] = '< 6 months' 

        try:
            pred = model.predict(temp_input_df) 
            pred_salary = float(pred[0]) if isinstance(pred, (list, pd.Series, np.ndarray)) and len(pred) > 0 else float(pred)
            
            realistic_adjustment_factor = 0.90 
            center_salary = pred_salary * realistic_adjustment_factor
            center_salary = max(180000.0, min(center_salary, 1500000.0))
        except Exception as e:
            st.error(f"ML Model Prediction Failed: {e}. Using base estimate.")
            center_salary = 300000.0 
            
    center_salary = float(center_salary)
    range_offset = max(center_salary * 0.10, 25000.0)
    salary_min = round((center_salary - range_offset) / 1000) * 1000
    salary_max = round((center_salary + range_offset) / 1000) * 1000
    salary_min = max(180000.0, salary_min)
    
    recs = None
    gemini_prompt = build_gemini_prompt(salary_min, salary_max, input_row["Job_Role_Level"], input_row["District"])
    gemini_response_raw = call_gemini(gemini_prompt) 
    
    if gemini_response_raw: recs = parse_json_array(gemini_response_raw)
    if not recs: recs = fallback_recs(input_row["Job_Role_Level"])
    
    return center_salary, salary_min, salary_max, recs

# --- MAIN PAGE FUNCTION ---
def show_salary_predictor_page():
    # 1. Initialize ALL required session state variables
    if 'prediction_count' not in st.session_state:
        st.session_state.prediction_count = 0
    if 'prediction_done' not in st.session_state:
        st.session_state.prediction_done = False
    if 'prediction_results' not in st.session_state:
        st.session_state.prediction_results = {}
    if 'prediction_error' not in st.session_state:
        st.session_state.prediction_error = None
    if 'custom_job_role_input_value' not in st.session_state:
        st.session_state.custom_job_role_input_value = ''
        
    # --- CSS STYLING ENGINE (Green/Dark Theme & Card Styled Inputs) ---
    st.markdown("""
    <style>
    /* --- IMPORT FONTS --- */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- RESET & VARIABLES --- */
    * { box-sizing: border-box; }

    :root {
        /* Color Palette - Neon Green Theme */
        --primary: #00E676;        /* Bright Neon Green */
        --primary-hover: #69F0AE;  /* Lighter Green */
        --primary-dim: rgba(0, 230, 118, 0.15);
        --secondary: #2979FF;      /* Blue Accent for gradients */

        --bg-dark: #020617;        /* Deepest Blue/Black */
        --bg-card: #0F172A;        /* Slate Dark */
        --bg-card-hover: #1E293B;  /* Lighter Slate */

        --text-main:#00E5FF;      /* White-ish */
        --text-secondary: #CBD5E1; /* Light Gray-Blue */
        --text-muted: #94A3B8;     /* Muted Gray */

        --border-color: #334155;
        --border-glow: rgba(0, 230, 118, 0.4);
        
        --shadow-card: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }

    /* --- GLOBAL STREAMLIT OVERRIDES --- */
    .stApp {
        background-color: var(--bg-dark);
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        background-attachment: fixed;
        font-family: 'Outfit', sans-serif;
        color: var(--text-main);
    }

    /* Hide default elements */
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }

    /* --- TYPOGRAPHY --- */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: var(--text-main) !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    p, li, span, div, label {
        font-family: 'Outfit', sans-serif;
        color: var(--text-main);
    }

    /* --- COMPONENT: HERO HEADER --- */
    .hero-header {
        text-align: center;
        padding: 50px 20px;
        margin-bottom: 30px;
        background: radial-gradient(circle at center, rgba(0, 230, 118, 0.1) 0%, transparent 70%);
        border-bottom: 1px solid var(--border-color);
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #FFF, var(--primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 230, 118, 0.3);
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-muted);
        font-weight: 300;
        max-width: 650px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* --- COMPONENT: FORM CONTAINER (CARD STYLE) --- */
    .form-container {
        /* Card Style Background */
        background: linear-gradient(145deg, var(--bg-card), #0b1120);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 40px;
        margin: 0 auto;
        max-width: 950px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Top Green Line Accent */
    .form-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 4px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        opacity: 0.8;
    }
    
    .form-container:hover {
        border-color: var(--border-glow);
        box-shadow: 0 0 20px var(--primary-dim);
    }

    .form-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
        color: var(--text-main);
    }

    .form-subtitle {
        color: var(--text-muted);
        text-align: center;
        margin-bottom: 3rem;
    }

    /* --- INPUT FIELDS & ICONS (CARD STYLING APPLIED HERE) --- */
    .input-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--primary);
        margin-bottom: 8px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
        padding-left: 28px;
    }
    
    .input-label::before {
        content: '';
        width: 20px; height: 20px;
        display: inline-block;
        position: absolute;
        left: 0; top: 50%;
        transform: translateY(-50%);
        filter: hue-rotate(250deg) brightness(1.2) saturate(1.5);
    }

    /* SVG Icons */
    .input-label.svg-district::before { content: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzIxOTZGMiI+PHBhdGggZD0iTTEyIDJDNy41ODggMiA0IDUuNTg4IDQgMTBzMy41ODggOCA4IDggOC0zLjU4OCA4LTgtMy41ODgtOC04LTh6bTAgMTRjLTMuMzEzIDAtNi0yLjY4Ny02LTZzMi42ODctNiA2LTYgNiAyLjY4NyA2IDYtMi42ODcgNi02IDZ6Ii8+PHBhdGggZD0iTTEyIDZhNCA0IDAgMTAwIDggNCA0IDAgMDAwLTh6Ii8+PC9zdmc+'); }
    .input-label.svg-company::before { content: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzIxOTZGMiI+PHBhdGggZD0iTTE5IDNINWMtMS4xIDAtMiAuOS0yIDJ2MTRjMCAxLjEuOSAyIDIgMmgxNGMxLjEgMCAyLS45IDItMlY1YzAtMS4xLS45LTItMi0yem0tMiAxNkg3VjloMTB2MTB6Ii8+PHBhdGggZD0iTTE2IDExaC0ydjJIMTB2LTJIOHY0aDh2LTR6Ii8+PC9zdmc+'); }
    .input-label.svg-role::before { content: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzIxOTZGMiI+PHBhdGggZD0iTTIwIDZoLTRWM2MwLTEuMS0uOS0yLTItMmgtNGMtMS4xIDAtMiAuOS0yIDJ2M0g0Yy0xLjEgMC0yIC45LTIgMnYxMmMwIDEuMS45IDIgMiAyaDE2YzEuMSAwIDItLjkgMi0yVjhjMC0xLjEtLjktMi0yLTJ6TTEwIDNoNHY0aC00VjN6bTggMTZINlYxMGgxMnY4em0wLTEwSDZWOGgxMnYyeiIvPjwvc3ZnPg=='); }
    .input-label.svg-internship::before { content: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzIxOTZGMiI+PHBhdGggZD0iTTE1IDFIN2MtMS4xIDAtMiAuOS0yIDJ2MThjMCAxLjEuOSAyIDIgMmgxMGMxLjEgMCAyLS45IDItMlYzYzAtMS4xLS45LTItMi0yem0wIDIwSDdWMTJoMTB2OXptMC0xMUg3VjNoMTB2N3oiLz48cGF0aCBkPSJNMTYgNmgydjJIMTZ6Ii8+PC9zdmc+'); }
    .input-label.svg-cgpa::before { content: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzIxOTZGMiI+PHBhdGggZD0iTTE5IDNINWMtMS4xIDAtMiAuOS0yIDJ2MTRjMCAxLjEuOSAyIDIgMmgxNGMxLjEgMCAyLS45IDItMlY1YzAtMS4xLS45LTItMi0yem0wIDE2SDU5VjVIMTl2MTR6Ii8+PHBhdGggZD0iTTcgMTBoMnY0SDd6bTQgMGgydjRoLTJ6bTQgMGgydjRoLTJ6Ii8+PC9zdmc+'); }
    .input-label.svg-college::before { content: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzIxOTZGMiI+PHBhdGggZD0iTTUgMTNoM3Y5SDF2LTlsMy0yIDMtMnptNyAwaDN2OWgtM3YtOWwzLTIgMy0yem03IDBoM3Y5aC0zdi05bDMtMiAzLTJ6Ii8+PHBhdGggZD0iTTEyIDFsMTIgNXYxNUgwVjZMMTIgMXoiLz48L3N2Zz4='); }

    /* --- INPUT WIDGET OVERRIDES (Fix Text Visibility) --- */
    /* Target Selectbox & TextInput containers to have Card Styling */
    .stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div {
        background-color: white !important; /* Dark Slate background */
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        color: #F8FAFC !important; /* Bright White text */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease;
    }

    /* Hover effect for inputs */
    .stSelectbox > div > div:hover, .stTextInput > div > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 10px var(--primary-dim) !important;
        transform: translateY(-2px);
    }

    /* Force text color inside input boxes */
    .stTextInput input, .stNumberInput input {
        color: #FFFFFF !important;
    }
    
    /* Force text color for selected value in dropdown */
    .stSelectbox div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* Fix Dropdown Menu Options (Dark Background, White Text) */
    ul[data-baseweb="menu"] {
        background-color: #0F172A !important;
        border: 1px solid var(--border-color) !important;
    }
    
    li[data-baseweb="option"] {
        color: #FFFFFF !important;
        background-color: #0F172A !important;
    }
    
    li[data-baseweb="option"]:hover {
        background-color: #1E293B !important;
        color: var(--primary) !important;
    }

    .stSelectbox > label, .stTextInput > label { display: none; }

    /* --- BUTTONS --- */
    /* Primary Action Button (Predict) */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, var(--primary) 0%, #00C853 100%) !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3) !important;
        width: 100%;
        margin-top: 20px;
    }

    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0, 230, 118, 0.5) !important;
    }

    /* Secondary / Navigation Buttons */
    .stButton > button {
        background-color: var(--bg-card) !important;
        color: var(--primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        border-color: var(--primary) !important;
        background-color: var(--bg-card-hover) !important;
    }

    /* --- RESULTS SECTION --- */
    .results-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 40px;
        margin: 20px auto;
        max-width: 950px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        animation: fadeIn 0.6s ease-out;
    }

    .salary-range-display {
        background: radial-gradient(circle at center, rgba(0, 230, 118, 0.1) 0%, transparent 70%);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .salary-amount {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(to right, #ffffff, var(--primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
        text-shadow: 0 10px 30px rgba(0, 230, 118, 0.2);
    }

    .salary-range {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-muted);
        font-size: 1.1rem;
        background: rgba(255, 255, 255, 0.05);
        padding: 5px 15px;
        border-radius: 8px;
        display: inline-block;
    }

    /* --- RECOMMENDATION CARDS --- */
    .recommendations-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .rec-card {
        background: linear-gradient(145deg, var(--bg-card), #0b1120);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .rec-card:hover {
        transform: translateY(-6px);
        border-color: var(--primary);
        box-shadow: 0 10px 25px rgba(0, 230, 118, 0.15);
    }

    .rec-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.5rem;
    }

    .rec-reason {
        color: var(--text-muted);
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .rec-priority {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }

    .priority-high {
        background: rgba(0, 230, 118, 0.2);
        color: var(--primary);
        border: 1px solid var(--primary);
    }

    .priority-medium {
        background: rgba(41, 121, 255, 0.2);
        color: var(--secondary);
        border: 1px solid var(--secondary);
    }

    .rec-link {
        display: block;
        text-align: center;
        background: var(--bg-card-hover);
        color: var(--primary);
        padding: 0.6rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid var(--border-color);
        transition: all 0.2s;
    }

    .rec-link:hover {
        background: var(--primary);
        color: #000;
        border-color: var(--primary);
    }

    /* --- QUOTA INDICATOR --- */
    .quota-indicator {
        position: fixed;
        bottom: 20px; right: 20px;
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid var(--primary);
        border-radius: 30px;
        padding: 10px 20px;
        display: flex; align-items: center; gap: 10px;
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.2);
        z-index: 1000;
    }
    
    .quota-text { color: var(--text-main); font-size: 0.9rem; font-weight: 600; }
    .quota-number { color: var(--primary); font-weight: 800; font-size: 1.1rem; }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .form-container, .results-container { padding: 1.5rem; margin: 1rem; }
        .salary-amount { font-size: 3rem; }
        .input-grid { grid-template-columns: 1fr; }
        .hero-title { font-size: 2.5rem; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 2. Add Back to Home Button
    col_nav, col_title = st.columns([1, 5])
    with col_nav:
        if st.button("← Home", key="salary_back_btn"):
            st.session_state["current_page"] = "Home"
            st.rerun()
    
    # --- HERO SECTION HTML ---
    st.markdown("""
        <div class="hero-header">
            <h1 class="hero-title">Salary Predictor</h1>
            <p class="hero-subtitle">
                <span style="color: #00E676; font-weight: 600;">AI-Powered</span> Compensation Intelligence for BCA Graduates.<br>
                Stop guessing. Know your true market value instantly.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- LOAD DATA AND CREATE OPTIONS ---
    train_df = load_training_data()
    
    if train_df is None: 
        st.stop()
        
    districts = get_options(train_df, "District", ["Thane", "Pune", "Mumbai Suburban", "Other"])
    
    job_roles_options_full = get_options(train_df, "Job_Role_Level", ["Software Developer - Graduate Engineer Trainee (GET)", "IT Support Specialist - Service Desk Analyst"])
    job_roles_options = [role for role in job_roles_options_full if role != "Other"]
    if "Not Listed" not in job_roles_options:
        job_roles_options.append("Not Listed")
        
    company_types = get_options(train_df, "Company_Type", ["Service-Based MNC", "Startup", "Product-Based MNC", "Mid-Sized Indian Co.", "Other"])
    internship_opts = get_options(train_df, "Internship_Exp", ["None", "< 6 months", "6-12 months", "> 1 year"])
    cgpa_opts = get_options(train_df, "CGPA", ["9.0+", "8.0-8.9", "7.0-7.9", "< 7.0"])
    college_tiers = get_options(train_df, "College_Tier", ["Tier-1", "Tier-2", "Tier-3"])
    
    model = load_model()
    if model is None: 
        st.stop() 
    
    user_role = st.session_state.get("role", "user") 
    is_admin = (user_role == "admin")
    PREDICTION_LIMIT = 5
    can_predict = is_admin or (st.session_state.prediction_count < PREDICTION_LIMIT)
    
    # --- Quota Indicator ---
    if not is_admin and st.session_state.prediction_count < PREDICTION_LIMIT:
        remaining = PREDICTION_LIMIT - st.session_state.prediction_count
        st.markdown(f"""
            <div class="quota-indicator">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00E676" stroke-width="2">
                    <path d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                </svg>
                <span class="quota-text">Predictions remaining:</span>
                <span class="quota-number">{remaining}</span>
            </div>
        """, unsafe_allow_html=True)
    
    # --- Input Form Section ---
    if not st.session_state.prediction_done:
        if st.session_state.prediction_error:
            st.error(f"❌ Prediction Failed: {st.session_state.prediction_error}")
            st.session_state.prediction_error = None 

        if can_predict:
            
            
            # Form Definition
            with st.form("salary_prediction_form"):
                # Two-Column Grid
                col1, col2 = st.columns(2)
                
                with col1:
                    # District Input
                    st.markdown('<div class="input-label svg-district">District</div>', unsafe_allow_html=True)
                    district = st.selectbox(
                        "", options=districts, index=0, key="sb_district", label_visibility="collapsed"
                    )
                    
                    # Company Type Input
                    st.markdown('<div class="input-label svg-company">Company Type</div>', unsafe_allow_html=True)
                    company_type = st.selectbox(
                        "", options=company_types, index=0, key="sb_company", label_visibility="collapsed"
                    )
                    
                    # Job Role Input
                    st.markdown('<div class="input-label svg-role">Job Role & Level</div>', unsafe_allow_html=True)
                    other_index = job_roles_options.index("Not Listed") if "Not Listed" in job_roles_options else 0
                    selected_role = st.selectbox(
                        "", options=job_roles_options, index=other_index, key="sb_role", label_visibility="collapsed"
                    )
                
                with col2:
                    # Internship Input
                    st.markdown('<div class="input-label svg-internship">Internship Experience</div>', unsafe_allow_html=True)
                    internship = st.selectbox(
                        "", options=internship_opts, index=0, key="sb_internship", label_visibility="collapsed"
                    )
                    
                    # CGPA Input
                    st.markdown('<div class="input-label svg-cgpa">CGPA Range</div>', unsafe_allow_html=True)
                    cgpa = st.selectbox(
                        "", options=cgpa_opts, index=0, key="sb_cgpa", label_visibility="collapsed"
                    )
                    
                    # College Tier Input
                    st.markdown('<div class="input-label svg-college">College Tier</div>', unsafe_allow_html=True)
                    college_tier = st.selectbox(
                        "", options=college_tiers, index=0, key="sb_college", label_visibility="collapsed"
                    )
                
                # Custom Role Input (Conditional)
                custom_role_text = ""
                if selected_role == "Not Listed":
                    st.markdown("---")
                    st.markdown('<div class="input-label">✍️ Enter Your Specific Job Role</div>', unsafe_allow_html=True)
                    custom_role_text = st.text_input(
                        "", value=st.session_state.get('custom_job_role_input_value', ''),
                        key="custom_job_role_input", label_visibility="collapsed",
                        placeholder="e.g., 'DevOps Engineer', 'Data Scientist', 'Product Manager'"
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Submit Button
                submitted = st.form_submit_button(" Generate Prediction", type="primary", use_container_width=True)
                
                # Prediction Logic
                if submitted:
                    # Validation for custom role
                    if selected_role == "Not Listed":
                        custom_input_value = custom_role_text.strip()
                        if not custom_input_value:
                            st.error("⚠️ Please enter a specific job role when 'Not Listed' is selected.")
                            st.stop()
                        final_job_role = custom_input_value
                        is_custom_role_flag = True
                        st.session_state['custom_job_role_input_value'] = custom_input_value
                    else:
                        final_job_role = selected_role
                        is_custom_role_flag = False
                        st.session_state['custom_job_role_input_value'] = ''
                    
                    # Create input row
                    input_row = {
                        "District": district, 
                        "Company_Type": company_type, 
                        "Job_Role_Level": final_job_role,
                        "Internship_Exp": internship, 
                        "CGPA": cgpa, 
                        "College_Tier": college_tier,
                    }
                    
                    # Perform Prediction
                    with st.spinner('Analyzing your profile and generating predictions...'):
                        try:
                            center_salary, salary_min, salary_max, recs = calculate_prediction_and_recs(
                                input_row, is_custom_role_flag, model, train_df
                            )
                        except Exception as e:
                            st.session_state.prediction_error = str(e)
                            st.session_state.prediction_done = False 
                            st.rerun() 
                    
                    # Store results
                    st.session_state.prediction_results = {
                        "pred_salary_min": salary_min, 
                        "pred_salary_max": salary_max, 
                        "pred_salary_center": center_salary, 
                        "input_row": input_row,
                        "recommendations": recs if recs else []
                    }
                    
                    if not is_admin:
                        st.session_state.prediction_count += 1
                        
                    st.session_state.last_prediction_summary = {
                        'Job Role': input_row["Job_Role_Level"].split(' - ')[0],
                        'CGPA': input_row["CGPA"],
                        'Salary Range': f"₹ {salary_min:,.0f} - ₹ {salary_max:,.0f}"
                    }

                    try:
                        # --- CORRECTED LINE: USE USER_INFO DICTIONARY ---
                        db.log_prediction(
                            st.session_state.get('user_info', {}).get('username', 'Guest'), 
                            f"₹ {salary_min:,.0f} - {salary_max:,.0f} (Center: {center_salary:,.0f})",
                            input_row["Job_Role_Level"]
                        )
                    except Exception as log_e:
                        print(f"Database logging failed: {log_e}")
                        
                    st.session_state.prediction_done = True
                    st.rerun()
            
            # Form Container End
            st.markdown('</div>', unsafe_allow_html=True) 
            
        else:
            # Prediction Limit Reached
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<div class="form-title">🔒 Prediction Limit Reached</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">
                    You have used all {st.session_state.prediction_count} of your {PREDICTION_LIMIT} predictions for this session.
                    <br><br>
                </div>
            """, unsafe_allow_html=True)
           
    # --- Results Display ---
    if st.session_state.prediction_done:
        with st.container():
            salary_min = st.session_state.prediction_results.get("pred_salary_min", 180000)
            salary_max = st.session_state.prediction_results.get("pred_salary_max", 250000)
            center_salary = st.session_state.prediction_results.get("pred_salary_center", 200000)
            input_row = st.session_state.prediction_results.get("input_row", {})
            recs = st.session_state.prediction_results.get("recommendations", [])
            job_role = input_row.get("Job_Role_Level", "N/A")
            
            
            
            # New Prediction Button
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← New Prediction", key="new_prediction_top", use_container_width=True):
                    st.session_state.prediction_done = False
                    st.session_state.prediction_results = {}
                    st.rerun()
            
            # Salary Range Display
            st.markdown("""
                <div class="salary-range-display">
                    <div style="color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;">
                        AI-Predicted Annual Salary Range
                    </div>
            """, unsafe_allow_html=True)
            
            # Create the FIXED Plotly figure (no gradient error)
            fig = go.Figure()
            
            # Add the main line with SOLID COLOR
            fig.add_trace(go.Scatter(
                x=[salary_min, center_salary, salary_max],
                y=[0, 0, 0],
                mode='lines+markers',
                line=dict(width=8, color='#00E676'),  # NEON GREEN
                marker=dict(
                    size=[0, 12, 0],
                    color=['#00E676', '#FFFFFF', '#00E676'],
                    line=dict(width=2, color='#FFFFFF')
                )
            ))
            
            fig.update_layout(
                showlegend=False,
                xaxis=dict(
                    showgrid=False, zeroline=False, visible=False,
                    range=[salary_min * 0.9, salary_max * 1.1]
                ),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=100,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Salary Amount Display
            st.markdown(f"""
                <div class="salary-amount">₹ {center_salary:,.0f}</div>
                <div class="salary-range">Range: ₹ {salary_min:,.0f} - ₹ {salary_max:,.0f}</div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Profile Summary
            st.markdown("### 📋 Your Profile Summary")
            summary_cols = st.columns(2)
            with summary_cols[0]:
                st.markdown(f"""
                    **📍 District:** {input_row.get('District', 'N/A')}  
                    **🏢 Company Type:** {input_row.get('Company_Type', 'N/A')}  
                    **💼 Job Role:** {job_role}
                """)
            with summary_cols[1]:
                st.markdown(f"""
                    **⏳ Experience:** {input_row.get('Internship_Exp', 'N/A')}  
                    **📊 CGPA:** {input_row.get('CGPA', 'N/A')}  
                    **🏫 College:** {input_row.get('College_Tier', 'N/A')}
                """)
            
            # Market Distribution Chart
            st.markdown("### 📊 Market Distribution vs Prediction")
            if train_df is not None:
                salaries_train = train_df[TARGET_COL]
                if not salaries_train.empty:
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=salaries_train, 
                        nbinsx=50, 
                        name='Market Distribution',
                        marker_color='rgba(0, 230, 118, 0.6)', # Green tint
                        opacity=0.7
                    ))
                    
                    # Add prediction range
                    fig_hist.add_vrect(
                        x0=salary_min, 
                        x1=salary_max, 
                        fillcolor="rgba(0, 230, 118, 0.3)", 
                        opacity=0.3, 
                        line_width=0,
                        annotation_text="Your Prediction",
                        annotation_position="top left",
                        annotation=dict(font=dict(color="#00E676", size=12), yshift=10)
                    )
                    
                    fig_hist.add_vline(
                        x=center_salary, 
                        line_width=2, 
                        line_dash="dash", 
                        line_color="#00E676",
                        annotation_text=f"Center: ₹{center_salary:,.0f}",
                        annotation_position="top right"
                    )
                    
                    fig_hist.update_layout(
                        xaxis_title_text='Annual Salary (INR)', 
                        yaxis_title_text='Frequency', 
                        bargap=0.1,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#FFFFFF', family='Inter', size=14),
                        legend=dict(
                            yanchor="top", y=0.95, xanchor="right", x=0.95,
                            bgcolor='rgba(15, 23, 42, 0.9)',
                            bordercolor='#334155', borderwidth=1,
                            font=dict(color='#FFFFFF', size=12)
                        ),
                        height=400,
                        margin=dict(l=50, r=50, t=30, b=50)
                    )
                    
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            # Recommendations Section
            st.markdown("### 💡 Recommended for Growth")
            st.markdown("Prioritized skills and certifications to reach higher salary tiers")
            
            if recs:
                st.markdown('<div class="recommendations-grid">', unsafe_allow_html=True)
                for i, r in enumerate(recs[:4]): 
                    if isinstance(r, dict):
                        priority_class = "priority-high" if r.get('priority', '').lower() == 'high' else "priority-medium"
                        st.markdown(f"""
                            <div class="rec-card">
                                <div class="rec-title">{r.get('name', 'N/A')}</div>
                                <div class="rec-reason">{r.get('reason', 'N/A')}</div>
                                <div class="rec-priority {priority_class}">{r.get('priority', 'Medium')} Priority</div>
                                <a href="{r.get('link', '#')}" target="_blank" class="rec-link">Start Learning →</a>
                            </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Feedback Section
            st.markdown("---")
            st.markdown("### 📝 Help Improve Our Predictions")
            with st.expander("Submit your actual offer details (optional)"):
                feedback_cols = st.columns(3)
                with feedback_cols[0]:
                    actual_offer = st.number_input(
                        "Actual Offer (₹)", min_value=100000, max_value=5000000, 
                        value=int(center_salary), step=50000
                    )
                with feedback_cols[1]:
                    accuracy_rating = st.select_slider(
                        "Prediction Accuracy", options=["Low", "Good", "High"], value="Good"
                    )
                with feedback_cols[2]:
                    if st.button("Submit Feedback", use_container_width=True):
                        st.success("Thank you for your feedback! This helps improve our AI model.")
                        try:
                            # Use session state username if available, else Guest
                            u_name = st.session_state.get('user_info', {}).get('username', 'Guest')
                            
                            db.log_feedback(
                                u_name,
                                input_row["Job_Role_Level"],
                                str(int(center_salary)),
                                str(actual_offer),
                                accuracy_rating
                            )
                            st.success("Thank you! Feedback recorded in System Database.")
                        except Exception as e:
                            st.error(f"Error logging feedback: {e}")
                        
            
            # Bottom Navigation
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Start New Prediction", key="new_prediction_bottom", use_container_width=True):
                    st.session_state.prediction_done = False
                    st.session_state.prediction_results = {}
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)


# --- EXECUTION ---
if __name__ == "__main__":
    # Initialize session state variables
    if 'logged_in' not in st.session_state: 
        st.session_state.logged_in = True
    if 'username' not in st.session_state: 
        st.session_state.username = "Test User"
    if 'role' not in st.session_state: 
        st.session_state.role = "user"
    if 'current_page' not in st.session_state: 
        st.session_state.current_page = "Salary Predictor"
    if 'prediction_count' not in st.session_state: 
        st.session_state.prediction_count = 0
    if 'prediction_done' not in st.session_state: 
        st.session_state.prediction_done = False
    if 'prediction_results' not in st.session_state: 
        st.session_state.prediction_results = {}
    if 'prediction_error' not in st.session_state: 
        st.session_state.prediction_error = None
    if 'custom_job_role_input_value' not in st.session_state: 
        st.session_state.custom_job_role_input_value = ''
    
    # Run the main function
    show_salary_predictor_page()