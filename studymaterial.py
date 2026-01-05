# studymaterial.py - Comprehensive Study Material Module
# Total Codebase: Real Company Logos & Polished UI Layout
# Author: Gemini (Refining User Vision)

import streamlit as st
import webbrowser
import time

# ==========================================
# 1. CONFIGURATION & STYLING ENGINE
# ==========================================

def inject_custom_css():
    """
    Injects the comprehensive CSS to handle the specific 'Mind Sprint' 
    Dark & Orange aesthetics with a perfect Grid Layout.
    """
    st.markdown(f"""
<style>
/* --- IMPORT FONTS --- */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

/* --- RESET & VARIABLES --- */
* {{
box-sizing: border-box;
}}

:root {{
/* Color Palette - Matching the image */
--primary: #FF9F1C;        /* Bright Orange */
--primary-hover: #FFB249;  /* Lighter Orange */
--primary-dim: rgba(255, 159, 28, 0.1);

--bg-dark: #020617;        /* Deepest Blue/Black */
--bg-card: #0F172A;        /* Slate Dark */
--bg-card-hover: #1E293B;  /* Lighter Slate */

--text-main: #F8FAFC;      /* White-ish */
--text-muted: #94A3B8;     /* Gray */
--text-dark: #020617;      /* Black for buttons */

--border-color: #334155;
--border-glow: rgba(255, 159, 28, 0.5);

--shadow-card: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
--shadow-glow: 0 0 20px rgba(255, 159, 28, 0.2);
}}

/* --- GLOBAL STREAMLIT OVERRIDES --- */
.stApp {{
background-color: var(--bg-dark);
/* Subtle Grid Background */
background-image: 
linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
background-size: 50px 50px;
font-family: 'Outfit', sans-serif;
}}

/* Hide default elements */
#MainMenu, header, footer {{visibility: hidden;}}
.block-container {{ padding-top: 2rem; padding-bottom: 5rem; }}

/* --- TYPOGRAPHY --- */
h1, h2, h3, h4, h5, h6 {{
font-family: 'Outfit', sans-serif;
font-weight: 700;
color: var(--text-main);
}}

p, li, span, div {{
font-family: 'Outfit', sans-serif;
color: var(--text-main);
}}

/* --- COMPONENT: HEADER --- */
.hero-header {{
text-align: center;
padding: 40px 20px;
margin-bottom: 30px;
background: radial-gradient(circle at center, rgba(255, 159, 28, 0.15) 0%, transparent 70%);
}}

.hero-title {{
font-size: 3.5rem;
font-weight: 800;
letter-spacing: -1px;
margin-bottom: 10px;
background: linear-gradient(135deg, #FFF, #FF9F1C);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
text-shadow: 0 0 30px rgba(255, 159, 28, 0.3);
}}

.hero-subtitle {{
font-size: 1.2rem;
color: var(--text-muted);
font-weight: 300;
max-width: 600px;
margin: 0 auto;
}}

/* --- COMPONENT: SEARCH BAR --- */
.stTextInput > div > div > input {{
background-color: var(--bg-card) !important;
border: 1px solid var(--border-color) !important;
color: var(--text-main) !important;
border-radius: 12px !important;
padding: 15px 20px !important;
font-size: 1.1rem !important;
transition: all 0.3s ease !important;
}}

.stTextInput > div > div > input:focus {{
border-color: var(--primary) !important;
box-shadow: 0 0 0 2px var(--primary-dim) !important;
}}

/* --- COMPONENT: CATEGORY TABS (BUTTONS) --- */
.stButton > button {{
width: 100%;
background-color: var(--bg-card);
color: var(--text-muted);
border: 1px solid var(--border-color);
border-radius: 8px;
padding: 12px 24px;
font-weight: 600;
font-size: 0.9rem;
text-transform: uppercase;
letter-spacing: 1px;
transition: all 0.2s ease;
}}

.stButton > button:hover {{
border-color: var(--primary);
color: var(--primary);
background-color: var(--bg-card-hover);
transform: translateY(1px);
}}

.stButton > button:active, .stButton > button:focus {{
background-color: var(--primary);
color: var(--text-dark);
border-color: var(--primary);
box-shadow: 0 0 15px var(--primary);
}}

/* --- COMPONENT: COMPANY CARDS --- */
.company-card {{
background: linear-gradient(145deg, var(--bg-card), #0b1120);
border: 1px solid var(--border-color);
border-radius: 16px;
padding: 10px;
display: flex;
flex-direction: column;
align-items: center;
justify-content: space-between;
height: 280px; /* Fixed height for symmetry */
position: relative;
overflow: hidden;
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
}}

.company-card:hover {{
transform: translateY(-8px);
border-color: var(--primary);
box-shadow: var(--shadow-glow);
}}

.company-card::before {{
content: '';
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 4px;
background: linear-gradient(90deg, transparent, var(--primary), transparent);
opacity: 0;
transition: opacity 0.3s ease;
}}

.company-card:hover::before {{
opacity: 1;
}}

/* --- UPDATED: LOGO CONTAINER --- */
.card-logo-wrapper {{
width: 180px;
height: 250px;
background: black; /* White bg for logos */
border-radius: 16px; /* Soft square */
display: flex;
align-items: center;
justify-content: center;
margin-bottom: 15px;
padding: 10px; /* Padding so logo doesn't touch edge */
border: 1px solid rgba(255, 255, 255, 0.1);
transition: all 0.3s ease;
box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}}

.company-logo-img {{
width: 100%;
height: 100%;
object-fit: center; /* Ensures logo fits perfectly without distortion */
filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}}

.company-card:hover .card-logo-wrapper {{
border-color: var(--primary);
transform: scale(1.05);
box-shadow: 0 0 15px var(--primary-dim);
}}

.card-title {{
font-size: 1.4rem;
font-weight: 700;
margin: 0 0 5px 0;
color: var(--text-main);
}}

.card-category {{
font-size: 0.75rem;
text-transform: uppercase;
letter-spacing: 1.5px;
color: var(--text-muted);
background: rgba(255, 255, 255, 0.05);
padding: 4px 10px;
border-radius: 20px;
margin-bottom: 20px;
}}

/* --- COMPONENT: MODAL / DETAILS VIEW --- */
.details-container {{
background-color: var(--bg-card);
border: 1px solid var(--border-color);
border-radius: 24px;
padding: 40px;
margin-top: 20px;
box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
animation: fadeIn 0.4s ease-out forwards;
}}

/* Large Logo in Details View */
.details-logo-wrapper {{
width: 120px;
height: 120px;
background: white;
border-radius: 24px;
padding: 15px;
margin: 0 auto 20px auto;
display: flex;
align-items: center;
justify-content: center;
box-shadow: 0 0 30px rgba(0,0,0,0.5);
}}

@keyframes fadeIn {{
from {{ opacity: 0; transform: translateY(20px); }}
to {{ opacity: 1; transform: translateY(0); }}
}}

.resource-row {{
display: flex;
align-items: center;
justify-content: space-between;
background: rgba(30, 41, 59, 0.4);
padding: 20px;
border-radius: 12px;
margin-bottom: 15px;
border-left: 4px solid var(--primary);
transition: background 0.2s ease;
}}

.resource-row:hover {{
background: rgba(30, 41, 59, 0.8);
}}

.resource-info h4 {{
margin: 0 0 5px 0;
color: var(--primary);
font-size: 1.1rem;
}}

.resource-info p {{
margin: 0;
color: var(--text-muted);
font-size: 0.9rem;
}}

.url-tag {{
font-family: 'JetBrains Mono', monospace;
font-size: 0.75rem;
color: #64748B;
margin-top: 5px;
display: block;
}}

/* --- FOOTER --- */
.custom-footer {{
text-align: center;
padding: 40px 0;
margin-top: 60px;
border-top: 1px solid var(--border-color);
color: var(--text-muted);
font-size: 0.9rem;
}}

.custom-footer span {{
color: var(--primary);
font-weight: 600;
}}

/* Helper for spacing */
.spacer-20 {{ height: 20px; }}
.spacer-40 {{ height: 40px; }}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LAYER (UPDATED WITH CUSTOM LOGO SUPPORT)
# ==========================================

def get_companies_database():
    """
    Returns the complete dictionary of companies.
    'logo': Paste your image link directly in this field.
    """
    return {
        "TCS": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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", 
            "category": "it",
            "full_name": "Tata Consultancy Services",
            "description": "Global leader in IT services, consulting, and business solutions.",
            "hiring_modes": ["TCS NQT (National Qualifier Test)", "TCS Digital", "TCS Ninja"],
            "materials": [
                {"title": "TCS NQT - Aptitude & Logic (IndiaBIX)", "desc": "Comprehensive practice for numerical ability.", "url": "https://www.indiabix.com/aptitude/questions-and-answers/"},
                {"title": "TCS Coding Practice (GeeksforGeeks)", "desc": "Previous year coding questions and solutions.", "url": "https://www.geeksforgeeks.org/tcs-interview-preparation/"},
                {"title": "TCS Verbal Ability Guide", "desc": "English proficiency test preparation.", "url": "https://www.faceprep.in/tcs/tcs-verbal-ability/"}
            ]
        },
        "Infosys": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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",

            "category": "it",
            "full_name": "Infosys Limited",
            "description": "A global leader in next-generation digital services and consulting.",
            "hiring_modes": ["InfyTQ (Certification)", "HackWithInfy", "On-Campus"],
            "materials": [
                {"title": "InfyTQ Python/Java Course", "desc": "Official certification preparation guide.", "url": "https://infyspringboard.onwingspan.com/"},
                {"title": "Infosys Pseudocode Practice", "desc": "Crucial for the first round of selection.", "url": "https://www.faceprep.in/infosys/infosys-pseudocode-questions/"},
                {"title": "Infosys Interview Experiences", "desc": "Real interview questions from candidates.", "url": "https://www.geeksforgeeks.org/tag/infosys-interview-experience/"}
            ]
        },
        "Wipro": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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",

            "category": "it",
            "full_name": "Wipro Limited",
            "description": "Leading technology services and consulting company.",
            "hiring_modes": ["Wipro NLTH (Elite)", "Wipro Turbo", "WILP"],
            "materials": [
                {"title": "Wipro Elite NTH Patterns", "desc": "Exam pattern and syllabus breakdown.", "url": "https://prepinsta.com/wipro-nlth/syllabus/"},
                {"title": "Wipro Coding Questions", "desc": "Automata Fix and coding challenges.", "url": "https://www.faceprep.in/wipro/wipro-coding-questions/"}
            ]
        },
        "HCL": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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",

            "category": "it",
            "full_name": "HCL Technologies",
            "description": "Global technology company helping enterprises reimagine their businesses.",
            "hiring_modes": ["HCL First Careers", "Campus Drive"],
            "materials": [
                {"title": "HCL Numerical Ability", "desc": "Quantitative aptitude practice sets.", "url": "https://www.indiabix.com/aptitude/questions-and-answers/"},
                {"title": "HCL Technical Interview Questions", "desc": "C++, Java, and DBMS common questions.", "url": "https://www.javatpoint.com/hcl-interview-questions"}
            ]
        },
        "Accenture": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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",

            "category": "consulting",
            "full_name": "Accenture",
            "description": "Professional services company, providing strategy and consulting.",
            "hiring_modes": ["ASE (Associate SW Engineer)", "FSE (Full Stack Engineer)"],
            "materials": [
                {"title": "Accenture Cognitive Assessment", "desc": "Critical thinking and abstract reasoning.", "url": "https://www.prep.youth4work.com/placement-papers/accenture-test"},
                {"title": "Accenture Coding (FSE Role)", "desc": "Advanced DSA questions for higher packages.", "url": "https://takeuforward.org/interviews/accenture-coding-questions/"}
            ]
        },
        "Capgemini": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/png;base64,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",

            "category": "consulting",
            "full_name": "Capgemini",
            "description": "Leader in consulting, digital transformation, technology and engineering.",
            "hiring_modes": ["Exceller", "Senior Analyst"],
            "materials": [
                {"title": "Capgemini Game-Based Aptitude", "desc": "Unique game-based cognitive tests.", "url": "https://prepinsta.com/capgemini/game-based-aptitude/"},
                {"title": "Capgemini Pseudo Code", "desc": "Data structures and logic flow questions.", "url": "https://www.faceprep.in/capgemini/capgemini-pseudo-code-questions/"}
            ]
        },
        "IBM": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/png;base64,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",

            "category": "it",
            "full_name": "IBM",
            "description": "International Business Machines Corporation.",
            "hiring_modes": ["Associate Developer", "GBS Hiring"],
            "materials": [
                {"title": "IBM IPAT Test Guide", "desc": "Information Processing Aptitude Test logic.", "url": "https://www.assessmentday.co.uk/ibm-ipat.htm"},
                {"title": "IBM Number Series", "desc": "Specific number series logic practice.", "url": "https://www.indiabix.com/logical-reasoning/number-series/"}
            ]
        },
        "Cognizant": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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",

            "category": "it",
            "full_name": "Cognizant (CTS)",
            "description": "American multinational information technology services and consulting.",
            "hiring_modes": ["GenC", "GenC Elevate", "GenC Next"],
            "materials": [
                {"title": "Cognizant GenC Aptitude", "desc": "Standard quantitative and logical ability.", "url": "https://www.indiabix.com/"},
                {"title": "Automata Fix Questions", "desc": "Debugging logic errors in code.", "url": "https://prepinsta.com/cognizant/automata-fix/"}
            ]
        },
        "Amazon": {
            # PASTE YOUR IMAGE LINK HERE
            "logo":"data:image/png;base64,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",

            "category": "ecommerce",
            "full_name": "Amazon",
            "description": "Focuses on e-commerce, cloud computing, online advertising, and AI.",
            "hiring_modes": ["SDE Intern", "SDE-1", "Support Engineer"],
            "materials": [
                {"title": "Amazon Leadership Principles", "desc": "Essential for behavioral interviews.", "url": "https://www.amazon.jobs/en/principles"},
                {"title": "Amazon SDE Sheet (Striver)", "desc": "Top 150 Coding questions asked in Amazon.", "url": "https://takeuforward.org/interviews/amazon-interview-questions/"}
            ]
        },
        "Flipkart": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/png;base64,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",

            "category": "ecommerce",
            "full_name": "Flipkart",
            "description": "One of India's leading e-commerce marketplaces.",
            "hiring_modes": ["SDE-1", "Girls Wanna Code", "Grid Challenge"],
            "materials": [
                {"title": "Flipkart Machine Coding", "desc": "Design workable code in 90 mins.", "url": "https://workat.tech/machine-coding/article/flipkart-machine-coding-round-guide"},
                {"title": "Dynamic Programming Practice", "desc": "Key topic for Flipkart coding rounds.", "url": "https://leetcode.com/tag/dynamic-programming/"}
            ]
        },
        "Deloitte": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/png;base64,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",

            "category": "consulting",
            "full_name": "Deloitte",
            "description": "Audit, consulting, tax, and advisory services.",
            "hiring_modes": ["NLA (National Level Assessment)", "Campus"],
            "materials": [
                {"title": "Deloitte Versant Test", "desc": "English communication skills check.", "url": "https://www.youtube.com/results?search_query=deloitte+versant+test+preparation"},
                {"title": "Logical Reasoning", "desc": "Data interpretation and logic.", "url": "https://www.indiabix.com/logical-reasoning/data-sufficiency/"}
            ]
        },
        "Tech Mahindra": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/png;base64,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",

            "category": "it",
            "full_name": "Tech Mahindra",
            "description": "Indian multinational information technology services and consulting.",
            "hiring_modes": ["Elevate", "Campus"],
            "materials": [
                {"title": "TechM Aptitude + English", "desc": "Prepositions, articles, and basic math.", "url": "https://www.indiabix.com/verbal-ability/questions-and-answers/"},
                {"title": "Basic Coding Questions", "desc": "String manipulation and arrays.", "url": "https://www.javatpoint.com/tech-mahindra-interview-questions"}
            ]
        },
        "Mindtree": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/png;base64,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", 

            "category": "it",
            "full_name": "LTIMindtree",
            "description": "Global technology consulting and digital solutions company.",
            "hiring_modes": ["Campus", "Off-Campus"],
            "materials": [
                {"title": "Mindtree Coding", "desc": "Implementation and Bit Manipulation.", "url": "https://prepinsta.com/mindtree/coding/"}
            ]
        },
        "Oracle": {
            # PASTE YOUR IMAGE LINK HERE
            "logo": "data:image/jpeg;base64,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",
            "category": "it",
            "full_name": "Oracle",
            "description": "Database software and technology, cloud engineered systems.",
            "hiring_modes": ["G B U", "F S G B U"],
            "materials": [
                {"title": "Oracle SQL/DBMS Questions", "desc": "Deep dive into Database concepts.", "url": "https://www.geeksforgeeks.org/oracle-interview-experience/"},
                {"title": "AVL Trees & Graphs", "desc": "Advanced Data Structures.", "url": "https://www.programiz.com/dsa"}
            ]
        }
    }

def get_category_display_name(key):
    """Maps internal category keys to display names"""
    mapping = {
        'all': ' All Companies',
        'it': ' IT Services',
        'consulting': ' Consulting',
        'ecommerce': ' E-Commerce'
    }
    return mapping.get(key, key.title())

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def render_html_card(company_name, company_data, idx):
    """
    Renders the HTML structure for a single company card.
    Uses custom logo link from database.
    """
    category_label = get_category_display_name(company_data['category']).replace("", "").replace("", "").replace(" ", "")
    # Use the custom logo link provided in the database
    logo_url = company_data['logo']
    
    html = f"""
<div class="company-card">
<div style="text-align: center; width: 100%;">
<div style="display: flex; justify-content: center;">
<div class="card-logo-wrapper">
<img src="{logo_url}" class="company-logo-img" alt="{company_name} Logo" onerror="this.onerror=null; this.src='https://via.placeholder.com/80?text={company_name[0]}'">
</div>
</div>
<h3 class="card-title">{company_name}</h3>
<span class="card-category">{category_label}</span>
</div>

<div style="width: 100%; text-align: center; margin-top: 10px;">
<div style="font-size: 0.8rem; color: #64748B; margin-bottom: 10px;">
{len(company_data['materials'])} Resources Available
</div>
</div>
</div>
</div>
"""
    return html

def render_details_modal(company_name, company_data):
    """
    Renders the detailed view when a company is selected.
    Uses custom logo link.
    """
    logo_url = company_data['logo']
    
    # 1. Back Button Row
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("← Back", key="btn_back_details"):
            st.session_state.show_materials = False
            st.session_state.selected_company = None
            st.rerun()

    # 2. Main Details Container
    st.markdown(f"""
<div class="details-container">
<div style="text-align: center; border-bottom: 1px solid var(--border-color); padding-bottom: 30px; margin-bottom: 30px;">

<div class="details-logo-wrapper">
<img src="{logo_url}" class="company-logo-img" alt="{company_name} Logo">
</div>

<h1 style="color: var(--primary); font-size: 3rem; margin-bottom: 10px;">{company_data['full_name']}</h1>
<p style="font-size: 1.2rem; color: var(--text-muted); max-width: 700px; margin: 0 auto;">
{company_data['description']}
</p>
<div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
""", unsafe_allow_html=True)
    
    # Render Hiring Modes tags
    # Centering hack logic
    cols = st.columns(len(company_data['hiring_modes']) + 2) 
    for mode in company_data['hiring_modes']:
        st.markdown(f"""
<span style="
background: rgba(255, 255, 255, 0.1); 
padding: 6px 15px; 
border-radius: 20px; 
font-size: 0.85rem; 
border: 1px solid rgba(255, 255, 255, 0.2);
color: #E2E8F0;
"> {mode}</span>
""", unsafe_allow_html=True)
            
    st.markdown("</div></div><h3 style='margin-bottom: 20px;'> Curated Study Materials</h3>", unsafe_allow_html=True)

    # 3. Resources List
    if company_data['materials']:
        for idx, mat in enumerate(company_data['materials']):
            col_res_text, col_res_btn = st.columns([4, 1])
            
            with col_res_text:
                st.markdown(f"""
<div class="resource-row">
<div class="resource-info">
<h4>{mat['title']}</h4>
<p>{mat['desc']}</p>
<span class="url-tag">🔗 Source: {mat['url'][:40]}...</span>
</div>
</div>
""", unsafe_allow_html=True)
            
            with col_res_btn:
                # Vertically center the button relative to the row
                st.markdown("<div style='height: 25px'></div>", unsafe_allow_html=True)
                if st.button(f"OPEN ↗", key=f"open_res_{idx}_{company_name}"):
                    webbrowser.open_new_tab(mat['url'])
    else:
        st.info("No resources added for this company yet.")

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN PAGE LOGIC
# ==========================================

def study_materials():
    """
    Main entry point for the module.
    """
    # 1. Initialize State
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = 'all'
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    if 'show_materials' not in st.session_state:
        st.session_state.show_materials = False
    
    # 2. Inject Styles
    inject_custom_css()
    
    # 3. Load Data
    all_companies = get_companies_database()
    
    # 4. Render Layout
    
    # --- HEADER SECTION ---
    # Top Nav Row
    col_logo, col_home = st.columns([4, 1])
    with col_logo:
        st.markdown('<div style="color: var(--primary); font-weight: 800; font-size: 1.5rem; letter-spacing: -1px;">BCAsprint</div>', unsafe_allow_html=True)
    with col_home:
        if st.button(" Home", key="nav_home_top"):
            st.session_state.current_page = "Home"
            st.rerun()

    # Hero Banner
    if not st.session_state.show_materials:
        st.markdown("""
<div class="hero-header">
<h1 class="hero-title">Resource Library</h1>
<p class="hero-subtitle">
Master EveryAptitude Topic.Stop searching aimlessly.
</p>
</div>
""", unsafe_allow_html=True)

        # --- CONTROLS SECTION ---
        # Search
        st.markdown('<div style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
        search = st.text_input("", placeholder="🔍 Search for companies (e.g., TCS, Amazon, Wipro)...", key="search_main")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="spacer-40"></div>', unsafe_allow_html=True)

        # Categories
        c1, c2, c3, c4 = st.columns(4)
        buttons = [
            (" ALL", "all", c1),
            (" IT SERVICES", "it", c2),
            (" CONSULTING", "consulting", c3),
            (" E-COMMERCE", "ecommerce", c4)
        ]
        
        for label, cat_key, col in buttons:
            with col:
                # Highlight active button
                if st.session_state.selected_category == cat_key:
                    # In a real app we'd use CSS classes, here we just use the button state 
                    pass 
                if st.button(label, key=f"cat_{cat_key}", use_container_width=True):
                    st.session_state.selected_category = cat_key
                    st.rerun()

        st.markdown('<div class="spacer-40"></div>', unsafe_allow_html=True)

        # --- GRID SECTION ---
        # Filter Logic
        filtered_items = {}
        for name, data in all_companies.items():
            # Search Filter
            if search and search.lower() not in name.lower():
                continue
            # Category Filter
            if st.session_state.selected_category != 'all' and data['category'] != st.session_state.selected_category:
                continue
            filtered_items[name] = data

        # Grid Rendering
        if filtered_items:
            # Layout Configuration: 4 Columns per row
            COLS_PER_ROW = 4
            company_list = list(filtered_items.keys())
            
            # Use a container for the grid
            grid_container = st.container()
            
            with grid_container:
                for i in range(0, len(company_list), COLS_PER_ROW):
                    cols = st.columns(COLS_PER_ROW)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(company_list):
                            c_name = company_list[i + j]
                            c_data = filtered_items[c_name]
                            
                            with col:
                                # Render the visual card via HTML
                                st.markdown(render_html_card(c_name, c_data, i+j), unsafe_allow_html=True)
                                if st.button(f"View", key=f"btn_card_{c_name}", use_container_width=True):
                                    st.session_state.selected_company = c_name
                                    st.session_state.show_materials = True
                                    st.rerun()
                        else:
                            # Empty column filler if needed
                            pass
                    
                    # Add vertical space between rows
                    st.markdown("<div class='spacer-20'></div>", unsafe_allow_html=True)
        
        else:
            st.markdown("""
<div style="text-align: center; padding: 60px; color: var(--text-muted);">
<div style="font-size: 3rem; margin-bottom: 20px; opacity: 0.5;">🕸️</div>
<h3>No companies found matching your search.</h3>
<p>Try clearing the filters or searching for something else.</p>
</div>
""", unsafe_allow_html=True)

    # --- DETAILS SECTION ---
    else:
        # Show Details View
        if st.session_state.selected_company:
            render_details_modal(st.session_state.selected_company, all_companies[st.session_state.selected_company])


# Main Execution Check
if __name__ == "__main__":
    study_materials()