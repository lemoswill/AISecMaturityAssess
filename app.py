__import__('pysqlite3')
import sys
import os
import shutil
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import pandas as pd
import datetime
from modules import ui, storage, data, evidence, ai_engine, mappings, charts, reporting, roi, i18n

# --- Configuration ---
st.set_page_config(
    page_title="AI Security Maturity Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialization ---
storage.init_db()
if 'ui_style' not in st.session_state:
    st.session_state['ui_style'] = "Silicon Precision"
ui.load_custom_css(st.session_state['ui_style'])

# --- Session State ---
if 'responses' not in st.session_state:
    st.session_state['responses'] = {}
if 'ai_results' not in st.session_state:
    st.session_state['ai_results'] = {}
if 'provider_keys' not in st.session_state:
    st.session_state['provider_keys'] = {}
if 'provider_models' not in st.session_state:
    st.session_state['provider_models'] = {}

# --- Sidebar ---
st.sidebar.markdown("""
<div style="text-align: center; padding: 1.5rem 0 1rem 0; border-bottom: 1px solid #F1F5F9; margin-bottom: 1.5rem;">
    <div style="background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%); 
                width: 45px; height: 45px; border-radius: 12px; 
                display: flex; align-items: center; justify-content: center; 
                margin: 0 auto 12px auto; 
                box-shadow: 0 8px 16px rgba(37, 99, 235, 0.15);">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z" 
                  stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="white" fill-opacity="0.2"/>
            <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <h1 style="color: #0F172A; margin: 0; font-size: 0.95rem; font-weight: 800; letter-spacing: -0.01em;">AI Security</h1>
    <p style="color: #94A3B8; margin: 2px 0 0 0; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Precision Edition</p>
</div>
""", unsafe_allow_html=True)

# Navigation Section
st.sidebar.markdown("""
<style>
    /* Custom Radio Button Styling */
    div[data-testid="stSidebar"] .stRadio > label {
        display: flex !important;
        width: 100% !important;
        background: transparent;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    div[data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(255, 107, 0, 0.1);
        border-color: #FF6B00;
    }
    
    div[data-testid="stSidebar"] .stRadio > label[data-checked="true"] {
        background: linear-gradient(135deg, #FF6B00 0%, #FFA300 100%);
        border: none;
        font-weight: 600;
        color: white !important;
        box-shadow: 0 4px 12px rgba(255, 107, 0, 0.3);
    }
    div[data-testid="stSidebar"] .stRadio > label[data-checked="true"] p {
        color: white !important;
    }
</style>
<div style="margin-bottom: 1.5rem;">
    <p style="color: #64748B; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">Navigation</p>
</div>
""", unsafe_allow_html=True)

# Custom styled radio buttons
with st.sidebar:
    st.markdown("### NAVIGATION")
    # Determine default index based on session state override
    nav_options = [i18n.t("dashboard_tab"), i18n.t("assessment_tab"), i18n.t("evidence_tab"), i18n.t("roi_tab")]
    
    # Internal mapping to keep logic decoupled from translated strings
    nav_map = {
        i18n.t("dashboard_tab"): "Executive Dashboard",
        i18n.t("assessment_tab"): "Assessment",
        i18n.t("evidence_tab"): "Evidence Locker",
        i18n.t("roi_tab"): "ROI Calculator"
    }
    
    default_ix = 0
    if st.session_state.get('nav_override'):
        # Map internal name back to translated name for radio index
        rev_map = {v: k for k, v in nav_map.items()}
        target_nav_str = rev_map.get(st.session_state['nav_override'])
        if target_nav_str in nav_options:
            default_ix = nav_options.index(target_nav_str)
        del st.session_state['nav_override']

    page_selected = st.radio(
        "Navigation", 
        nav_options, 
        index=default_ix, 
        label_visibility="collapsed"
    )
    page = nav_map[page_selected]
    
    st.divider()
    st.markdown("---")

# Architecture Info Card
st.sidebar.markdown(f"""
<div style="background: #E0F2FE; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #0369A1;
            margin-bottom: 1rem;">
    <p style="color: #0369A1; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 8px 0;">Architecture</p>
    <p style="color: #0C4A6E; font-size: 0.85rem; margin: 0; line-height: 1.6;">
        <strong style="color: #0C4A6E;">Framework:</strong> NIST AI RMF<br>
        <strong style="color: #0C4A6E;">Controls:</strong> CSA AICM<br>
        <span style="display: block; margin-top: 4px; font-size: 0.8rem; font-weight: 600;">
            {"Organization" if "Organization" in st.session_state.get('scope_mode', 'Organization') else "Project: " + st.session_state.get('project_type_sel', 'Cloud')}
        </span>
    </p>
</div>
""", unsafe_allow_html=True)

# Demo Warning Banner
st.sidebar.markdown("""
<div style="background: #FEF3C7; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #D97706;
            margin-bottom: 1.5rem;">
    <p style="color: #92400E; font-size: 0.75rem; font-weight: 800; margin: 0 0 6px 0;">🧪 DEMO MODE ACTIVE</p>
    <p style="color: #78350F; font-size: 0.8rem; margin: 0; line-height: 1.5; font-weight: 500;">
        Data is <strong>not persisted</strong> between sessions. In production, this would integrate with <strong>PostgreSQL/Cloud Storage</strong> and <strong>Enterprise SSO</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Style & Appearance ---
st.sidebar.markdown(f'<p style="color: #64748B; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem;">{i18n.t("sidebar_settings")}</p>', unsafe_allow_html=True)

lang_choice = st.sidebar.radio(
    i18n.t("lang_selector"),
    ["English", "Português (Brasil)"],
    index=0 if st.session_state.get('lang', 'en') == "en" else 1,
    horizontal=True,
    label_visibility="collapsed"
)
new_lang = "en" if lang_choice == "English" else "pt"
if new_lang != st.session_state.get('lang'):
    st.session_state['lang'] = new_lang
    st.rerun()

theme_choice = st.sidebar.radio(
    "Select Interface Style",
    ["Silicon Precision", "Palo Alto Enterprise"],
    index=0 if st.session_state['ui_style'] == "Silicon Precision" else 1,
    help="Toggle between different enterprise design profiles. Palo Alto Enterprise offers a distinct high-contrast professional look.",
    label_visibility="collapsed"
)

if theme_choice != st.session_state['ui_style']:
    st.session_state['ui_style'] = theme_choice
    st.rerun()




# --- Main Content ---

if page == "Evidence Locker":
    ui.display_header("Evidence Locker", "Upload documents to enable AI Auto-Assessment")
    
    # 1. AI Provider Configuration
    st.markdown("""<div class="glass-card" style="padding: 2rem; margin-top: 1rem; border-left: 6px solid #4F46E5 !important;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(79, 70, 229, 0.1); padding: 10px; border-radius: 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2.5"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zM12 11V7m0 10v-4"/></svg>
            </div>
            <h3 style="margin: 0;">Intelligence Provider</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Provider Settings
    provider_options = ["OpenAI", "Gemini", "Perplexity", "Ollama (Local)"]
    provider_selected = st.selectbox("Intelligence Core", provider_options, index=0)
    provider_clean = provider_selected.split(" (")[0]
    st.session_state['ai_provider'] = provider_clean
    
    current_key = st.session_state.get('provider_keys', {}).get(provider_clean, "")
    current_model = st.session_state.get('provider_models', {}).get(provider_clean, "")

    if provider_clean == "Ollama":
        col1, col2 = st.columns([2, 3])
        with col1:
            ollama_host = st.text_input("Ollama Host URL", value=current_key if current_key else "http://localhost:11434")
            st.session_state['provider_keys'][provider_clean] = ollama_host
        with col2:
            engine = ai_engine.get_engine()
            local_models = engine.list_local_models(ollama_host)
            if local_models:
                index = 0
                if current_model in local_models: index = local_models.index(current_model)
                ollama_model = st.selectbox("Select Local Model", local_models, index=index)
                st.session_state['provider_models'][provider_clean] = ollama_model
            else:
                ollama_model = st.text_input("Model Name (Manual)", value=current_model if current_model else "deepseek-r1")
                st.session_state['provider_models'][provider_clean] = ollama_model
    else:
        col1, col2 = st.columns(2)
        with col1:
            new_key = st.text_input(f"{provider_clean} API Key", value=current_key, type="password")
            st.session_state['provider_keys'][provider_clean] = new_key
            st.session_state['api_key'] = new_key
            
            # Test Connection Button
            if st.button("🔌 Test Connection", width='stretch'):
                with st.spinner("Validating..."):
                    engine = ai_engine.get_engine()
                    success, msg = engine.validate_api_key(new_key, provider_clean, st.session_state['provider_models'].get(provider_clean))
                    if success:
                        st.success("✅ Key Validated")
                    else:
                        st.error(f"❌ {msg}")
                        
        with col2:
            default_model = "gpt-3.5-turbo" if provider_clean == "OpenAI" else "gemini-pro" if provider_clean == "Gemini" else "sonar"
            new_model = st.text_input("Model Name", value=current_model if current_model else default_model)
            st.session_state['provider_models'][provider_clean] = new_model
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # 2. File Upload
    st.markdown("""<div class="glass-card" style="padding: 2rem; border-left: 6px solid #2563EB !important;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(37, 99, 235, 0.1); padding: 10px; border-radius: 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.5"><path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
            </div>
            <h3 style="margin: 0;">Document Ingestion</h3>
        </div>
        <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 1.5rem;">Supply security policies, architecture reviews, or audit logs to fuel the AI analysis.</p>
    """, unsafe_allow_html=True)
    
    col_up, col_tag = st.columns([3, 1])
    with col_up:
        uploaded_files = st.file_uploader("Drop PDF/Text files here", type=['pdf', 'txt', 'md'], accept_multiple_files=True, label_visibility="collapsed")
    with col_tag:
        framework_tag = st.selectbox("Assign Framework", ["NIST AI RMF", "CSA AICM", "ISO 42001", "Internal Policy"], index=0)
        
    if uploaded_files:
        if st.button(f"⚡ Index {len(uploaded_files)} Resources", type="primary"):
            with st.spinner("Processing Intelligence..."):
                engine = ai_engine.get_engine()
                for up_file in uploaded_files:
                    saved_path = evidence.save_uploaded_file(up_file, framework_tag=framework_tag)
                    if saved_path:
                        success, _ = engine.ingest_file(up_file.name, framework_tag=framework_tag)
            st.success("Indexing Complete!")
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # 3. View Index
    st.markdown("### 📚 Intelligence Assets (Knowledge Base)")
    st.markdown('<p style="color: #64748B; font-size: 0.85rem; margin-top: -10px; margin-bottom: 20px;">Documents indexed for AI Auto-Assessment logic.</p>', unsafe_allow_html=True)
    
    files = evidence.list_evidence_files()
    if files:
        # Filter out .json metadata files for the list
        asset_files = [f for f in files if not f.endswith('.json')]
        
        if asset_files:
            # Build Metadata Table
            metadata_list = []
            for f in asset_files:
                meta = evidence.get_metadata(f)
                metadata_list.append({
                    "Document Name": f,
                    "Type": meta.get('type', 'N/A'),
                    "Framework": meta.get('framework', 'NIST'),
                    "Upload Date": meta.get('upload_date', 'N/A'),
                    "Uploaded By": meta.get('uploaded_by', 'System')
                })
            
            st.dataframe(pd.DataFrame(metadata_list), width='stretch', hide_index=True)
        else:
            st.info("Knowledge base is empty.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 4. Document Repository (Audit Trail)
        st.markdown("### 📜 Document Repository (Audit Trail)")
        st.markdown('<p style="color: #64748B; font-size: 0.85rem; margin-top: -10px; margin-bottom: 20px;">Regulatory record of all materials provided for this assessment.</p>', unsafe_allow_html=True)
        
        for f in asset_files:
            st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 15px; border-radius: 10px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
                        <span style="color: #334155; font-size: 0.9rem; font-weight: 500;">{f}</span>
                    </div>
                    <span style="background: #E0F2FE; color: #0369A1; font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; font-weight: 600;">VERIFIED</span>
                </div>
            """, unsafe_allow_html=True)
            
        if st.button("🗑️ Wipe Knowledge Base", type="secondary"):
             engine = ai_engine.get_engine()
             if engine.reset_db():
                 if os.path.exists(evidence.EVIDENCE_DIR):
                     shutil.rmtree(evidence.EVIDENCE_DIR)
                     os.makedirs(evidence.EVIDENCE_DIR)
                 st.rerun()
    else:
        st.info("No documents indexed yet.")

if page == "Assessment":
    # Global Context Banner (for screenshots/presentations)
    project_ctx = st.session_state.get('project_name', 'Demo Project')
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%); 
                    border-left: 4px solid #0EA5E9; 
                    padding: 8px 16px; 
                    margin-bottom: 12px; 
                    border-radius: 6px; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;">
            <span style="font-size: 0.85rem; color: #0C4A6E; font-weight: 600;">📋 {project_ctx} | Framework: NIST AI RMF + CSA AICM</span>
            <span style="font-size: 0.75rem; color: #0369A1;">Snapshot: {datetime.date.today().strftime("%Y-%m-%d")}</span>
        </div>
    """, unsafe_allow_html=True)

    # Subtle "Cloning Mode" / "Scenario Composer" Banner
    if st.session_state.get('cloning_from'):
        st.markdown(f"""
            <div style="background: rgba(79, 70, 229, 0.05); 
                        border: 1px dashed #4F46E5; 
                        padding: 12px 20px; 
                        border-radius: 10px; 
                        margin: 1.5rem 0; 
                        display: flex; 
                        align-items: center; 
                        gap: 12px;">
                <div style="background: #4F46E5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 800; text-transform: uppercase;">Draft Mode</div>
                <div style="color: #4338CA; font-size: 0.9rem; font-weight: 500; flex: 1;">
                    You are drafting a <strong>new scenario</strong> based on historical data from <strong>{st.session_state['cloning_from']}</strong>. 
                    <span style="color: #6366F1; font-size: 0.8rem; display: block; margin-top: 2px;">Changes will be saved as a fresh snapshot.</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("✖️ Cancel Draft & Clear Data", key="cancel_cloning", help="Exit cloning mode and clear loaded responses"):
            del st.session_state['cloning_from']
            if 'responses' in st.session_state: st.session_state['responses'] = {}
            # Also clear individual keys if needed, but 'responses' is the main one.
            # Actually, the widgets use unique_id keys. It's safer to just rerun and hope they clear if not in state.
            st.rerun()
    
    ui.display_header("AI Security Maturity Assessment", "NIST AI RMF mapped to CSA AICM Controls")
    
    # --- Scope Tabs ---
    st.markdown("""
<style>
    /* Custom Tab Styling for Scope Selection */
    div[data-baseweb="tab-list"] {
        gap: 10px;
        margin-bottom: 2rem;
    }
    div[data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    div[data-baseweb="tab"]:hover {
        background-color: #E2E8F0;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        background-color: #EFF6FF !important;
        border: 2px solid #2563EB !important;
        color: #1E3A8A !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.1), 0 2px 4px -1px rgba(37, 99, 235, 0.06);
    }
    div[data-baseweb="tab"][aria-selected="true"] p {
        color: #1E3A8A !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

    # --- Render Sub-Tabs (State-Controlled for Programmatic Loading) ---
    sub_tabs = {
        "Enterprise": i18n.t("tab_enterprise"),
        "Cloud": i18n.t("tab_cloud"),
        "SaaS": i18n.t("tab_saas")
    }
    
    # Initialize session state for sub-tab selection if not present
    if 'assessment_tab_selection' not in st.session_state:
        st.session_state['assessment_tab_selection'] = "Enterprise"
        
    # Visual Selector for "Tabs"
    selected_sub_tab_key = st.radio(
        "Assessment Category",
        options=list(sub_tabs.keys()),
        index=list(sub_tabs.keys()).index(st.session_state.get('assessment_tab_selection', 'Enterprise')),
        format_func=lambda x: sub_tabs[x],
        horizontal=True,
        help="Switch between Organization-wide (Enterprise) and Project-specific security profiles.",
        key="assessment_tab_selector", # Unique key
        label_visibility="collapsed"
    )
    # Sync back to state
    st.session_state['assessment_tab_selection'] = selected_sub_tab_key
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Logic: We will wrap the core assessment rendering in a function.
    def render_assessment_view(scope_key, type_key, label_override):
        # Update Session State for persistence (used in sidebar etc)
        # Note: This might jitter if multiple tabs run. 
        # Actually, for the Sidebar Info card to be correct, we technically need to know what the USER looks at.
        # But Streamlit runs generic script.
        # Let's set local variables for the rendering and ignore global session state for 'display' unless inside the button callbacks.
        
        # Get Filtered Data
        active_data = data.get_controls_for_scope(scope_key, type_key)
        
        # --- Silicon Precision Hero Section ---
        st.markdown(f"""
        <div class="glass-card" style="padding: 1.5rem; margin-top: 0.5rem; border-left: 6px solid #2563EB !important;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%); 
                            padding: 12px; 
                            border-radius: 12px;
                            box-shadow: 0 8px 15px rgba(37, 99, 235, 0.2);">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z" 
                              stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="white" fill-opacity="0.15"/>
                        <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div style="flex: 1;">
                    <h1 style="color: #0F172A; margin: 0; font-size: 1.4rem;">AI Security Maturity <span style="opacity:0.5; font-weight:400;">| {label_override}</span></h1>
                    <p style="color: #64748B; margin: 4px 0 0 0; font-size: 0.9rem; font-weight: 500;">
                        Automated Assessment based on NIST AI RMF & CSA AICM ({type_key.title() if scope_key == 'project' else 'Macro'}).
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- Smart CTA Logic ---
        files = evidence.list_evidence_files()
        has_evidence = len(files) > 0
        
        if not has_evidence:
            st.warning("⚠️ **No evidence uploaded yet.**")
        else:
            st.success(f"✅ **Intelligence Engine Online** - {len(files)} document(s) indexed")
            
            # --- AI Command Center Trigger ---
            available_domains = list(active_data.keys())
            
            col_dom, col_act = st.columns([3, 1])
            with col_dom:
                selected_domain = st.selectbox(
                    "Choose NIST Function to Analyze",
                    available_domains,
                    key=f"sel_dom_{scope_key}_{type_key}",
                    format_func=lambda x: f"{x} - {data.get_nist_functions()[x]}",
                    label_visibility="collapsed"
                )
            
            with col_act:
                current_provider = st.session_state.get('ai_provider', 'OpenAI')
                provider_keys = st.session_state.get('provider_keys', {})
                active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
                
                if active_key:
                    if st.button(f"🚀 Analyze {selected_domain}", key=f"btn_analyze_{scope_key}_{type_key}", type="primary", width='stretch'):
                        st.session_state['trigger_bulk_assess'] = selected_domain
                        st.session_state['active_tab_context'] = (scope_key, type_key) # Track where we came from
                        st.rerun()
                else:
                    st.button("🔑 Key Required", key=f"btn_lock_{scope_key}_{type_key}", type="secondary", width='stretch', disabled=True)
        
        st.markdown("---")
    
        # --- Maturity Journey (Phase Tracker) ---
        st.markdown(f"""<h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
            {i18n.t("journey_header")}
        </h3>""", unsafe_allow_html=True)
        
        waves = data.get_maturity_waves()
        wave_names = list(waves.values())
        wave_options = [i18n.t("all_waves")] + wave_names
        
        # Load CSS (already loaded globally, but ensuring scope)
        
        col_wave, _ = st.columns([1, 2])
        with col_wave:
            selected_wave_label = st.selectbox(
                i18n.t("phase_label"),
                wave_options,
                index=1,
                key=f"wave_sel_{scope_key}_{type_key}",
                label_visibility="collapsed"
            )
        
        # Local wave filter logic
        if selected_wave_label == i18n.t("all_waves"):
            selected_wave_id = None
        else:
            selected_wave_id = next(k for k, v in waves.items() if v == selected_wave_label)
        
        # --- Project Name & Progress Indicator ---
        col_name, col_progress = st.columns([2, 1])
        
        with col_name:
            project_name = st.text_input(i18n.t("project_name_label"), placeholder=i18n.t("project_name_placeholder"), key=f"proj_name_{scope_key}_{type_key}")
        
        with col_progress:
            total_controls = 0
            completed_controls = 0
            
            for func in active_data:
                for subcat_key in active_data[func]:
                    for control in active_data[func][subcat_key]['csa_controls']:
                        if selected_wave_id is not None and control.get('wave', 2) != selected_wave_id:
                            continue
                        
                        total_controls += 1
                        unique_id = f"score_{scope_key}_{type_key}_{subcat_key}_{control['id']}"
                        val = st.session_state.get(unique_id, 0)
                        
                        if isinstance(val, int) and val > 0:
                            completed_controls += 1
                        elif isinstance(val, str) and "(" in val:
                            try:
                                score_num = int(val.split('(')[-1].strip(')'))
                                if score_num > 0:
                                    completed_controls += 1
                            except:
                                pass
            
            completion_pct = (completed_controls / total_controls * 100) if total_controls > 0 else 0
            
            st.metric(
                label=f"{i18n.t('progress_label')} ({selected_wave_label})", 
                value=f"{completed_controls}/{total_controls}", 
                delta=f"{completion_pct:.0f}%",
                delta_color="normal"
            )
            st.progress(completion_pct / 100)
        
        # --- Save & Download Button ---
        if st.button(i18n.t("save_btn"), key=f"save_btn_{scope_key}_{type_key}", type="primary", width='stretch'):
            if not project_name:
                st.error("⚠️ Please enter a project name before saving.")
            else:
                final_responses = []
                for func in active_data:
                    for subcat_key in active_data[func]:
                        for control in active_data[func][subcat_key]['csa_controls']:
                            unique_id = f"score_{scope_key}_{type_key}_{subcat_key}_{control['id']}"
                            val = st.session_state.get(unique_id, 0)
                            
                            score = 0
                            if isinstance(val, int): score = val
                            elif isinstance(val, str) and "(" in val:
                                try: score = int(val.split('(')[-1].strip(')'))
                                except: score = 0
                            
                            ai_data = st.session_state.get('ai_results', {}).get(unique_id, {})
                            final_responses.append({
                                "category": func,
                                "question_id": control['id'],
                                "score": score,
                                "notes": f"{ai_data.get('justification', '')}\nSources: {', '.join(ai_data.get('sources', [])) if ai_data.get('sources') else ''}",
                                "ai_justification": ai_data.get('justification', ''),
                                "ai_sources": ", ".join(ai_data.get('sources', [])) if ai_data.get('sources') else '',
                                "mapping": subcat_key
                            })
                
                # Calculate stats
                func_scores = {}
                for func in active_data:
                    func_total = 0
                    func_count = 0
                    for subcat_key in active_data[func]:
                        for control in active_data[func][subcat_key]['csa_controls']:
                            unique_id = f"score_{scope_key}_{type_key}_{subcat_key}_{control['id']}"
                            val = st.session_state.get(unique_id, 0)
                            score = 0
                            if isinstance(val, int): score = val
                            elif isinstance(val, str) and "(" in val:
                                try: score = int(val.split('(')[-1].strip(')'))
                                except: pass
                            func_total += score
                            func_count += 1
                    
                    func_scores[func] = func_total / func_count if func_count > 0 else 0
                
                avg_score = sum(func_scores.values()) / len(func_scores) if func_scores else 0
                level = "Initial"
                if avg_score > 1.5: level = "Defined"
                if avg_score > 3.0: level = "Managed"
                if avg_score > 4.5: level = "Optimized"
                
                storage.save_assessment(project_name, final_responses, avg_score, level, scope=scope_key, project_type=type_key)
                if 'cloning_from' in st.session_state:
                    del st.session_state['cloning_from']
                
                st.success("✅ Assessment Saved Successfully!")
                st.rerun()
                
                csv_buffer = io.StringIO()
                pd.DataFrame(final_responses).to_csv(csv_buffer, index=False)
                
                st.success(f"✅ Assessment saved for **{project_name}**!")
                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv_buffer.getvalue(),
                    file_name=f"{project_name.replace(' ', '_')}_assessment.csv",
                    mime="text/csv",
                    key=f"dl_btn_{scope_key}_{type_key}"
                )
                st.balloons()
        
        st.markdown("---")
        
        # --- Handle Bulk Trigger ---
        if 'trigger_bulk_assess' in st.session_state and st.session_state.get('active_tab_context') == (scope_key, type_key):
             target_func = st.session_state['trigger_bulk_assess']
             # Reset immediately to avoid loop, or manage carefully. 
             # Safe to keep for one run.
             del st.session_state['trigger_bulk_assess']
             
             st.info(f"🤖 Starting AI analysis for **{target_func}**...")
             current_provider = st.session_state.get('ai_provider', 'OpenAI')
             provider_keys = st.session_state.get('provider_keys', {})
             active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
             
             if active_key:
                target_controls = []
                for sk, sd in active_data[target_func].items():
                    c_list = sd.get('csa_controls', [])
                    if selected_wave_id is not None:
                         target_controls.extend([(sk, c) for c in c_list if c.get('wave', 2) == selected_wave_id])
                    else:
                         target_controls.extend([(sk, c) for c in c_list])
                
                if target_controls:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    engine = ai_engine.get_engine()
                    active_model = st.session_state.get('provider_models', {}).get(current_provider)
                    
                    for idx, (sk, c) in enumerate(target_controls):
                        status_text.text(f"Analyzing {idx+1}/{len(target_controls)}: {c['id']}...")
                        progress_bar.progress((idx + 1) / len(target_controls))
                        unique_id = f"score_{scope_key}_{type_key}_{sk}_{c['id']}"
                        try:
                            res = engine.assess_control(c['text'], c.get('help', ''), active_key, provider=current_provider, model_name=active_model)
                            st.session_state['ai_results'][unique_id] = res
                            if 'score' in res and isinstance(res['score'], int):
                                st.session_state['responses'][unique_id] = res['score']
                                options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
                                st.session_state[unique_id] = options[max(0, min(5, res['score']))]
                        except Exception as e:
                            print(f"Error: {e}")
                    
                    status_text.success(f"✅ {target_func} analysis complete!")
                    progress_bar.empty()
                    st.rerun()

        # --- Tabs for Functions ---
        func_tabs = st.tabs(list(active_data.keys()))
        
        for i, func in enumerate(active_data):
            with func_tabs[i]:
                st.markdown(f"### {func}: {data.get_nist_functions().get(func, '')}")
                
                # Bulk Button (Per-Tab) is redundant with Hero but kept for UX
                
                st.divider()
                
                subcats = active_data[func]
                has_visible_controls = False
                
                for subcat_key, subcat_data in subcats.items():
                    csa_controls = subcat_data.get('csa_controls', [])
                    if selected_wave_id is not None:
                        visible_controls = [c for c in csa_controls if c.get('wave', 2) == selected_wave_id]
                    else:
                        visible_controls = csa_controls
                    
                    if not visible_controls: continue
                    has_visible_controls = True
                    
                    # Subcat Header - Calculate progress
                    current_subcat_total = 0
                    responded_count = 0
                    for c in visible_controls:
                        unique_id = f"score_{scope_key}_{type_key}_{subcat_key}_{c['id']}"
                        val = st.session_state.get(unique_id, 0)
                        score = 0
                        if isinstance(val, int): 
                            score = val
                            if val > 0: responded_count += 1
                        elif isinstance(val, str):
                            try: 
                                score = int(val.split('(')[-1].strip(')'))
                                if score > 0: responded_count += 1
                            except: pass
                        current_subcat_total += score
                    subcat_avg = current_subcat_total / len(visible_controls) if visible_controls else 0
                    total_controls_in_subcat = len(visible_controls)
                    
                    # Enhanced expander header with progress
                    with st.expander(f"{subcat_key} – {responded_count} of {total_controls_in_subcat} responded"):
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; background: #F8FAFC; padding: 10px 15px; border-radius: 8px; border: 1px solid #E2E8F0;">
                                <span style="color: #64748B; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Subcategory Maturity</span>
                                <span style="color: #2563EB; font-weight: 800; font-size: 1.1rem;">{subcat_avg:.1f} / 5.0</span>
                            </div>
                            <p style="color: #475569; font-style: italic; font-size: 0.95rem; margin-bottom: 1.5rem;">{subcat_data['description']}</p>
                        """, unsafe_allow_html=True)
                        st.divider()
                        
                        for control in visible_controls:
                            unique_id = f"score_{scope_key}_{type_key}_{subcat_key}_{control['id']}"
                            
                            # AI Button
                            current_provider = st.session_state.get('ai_provider', 'OpenAI')
                            provider_keys = st.session_state.get('provider_keys', {})
                            active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
                            
                            if active_key:
                                col_btn, col_empty = st.columns([1, 4])
                                if col_btn.button("✨ Auto-Assess", key=f"btn_{unique_id}_{scope_key}_{type_key}", help=f"Analyze with {current_provider}"):
                                    # Logic...
                                    # Since this is replicated, we should assume the helper logic works the same
                                    # But we need access to engine etc.
                                    # For brevity in this chunk, I'll rely on the existing Session State.
                                    with st.spinner(f"Analyzing..."):
                                        engine = ai_engine.get_engine()
                                        active_model = st.session_state.get('provider_models', {}).get(current_provider)
                                        res = engine.assess_control(control['text'], control.get('help', ''), active_key, provider=current_provider, model_name=active_model)
                                        st.session_state['ai_results'][unique_id] = res
                                        if 'score' in res and isinstance(res['score'], int):
                                            st.session_state['responses'][unique_id] = res['score']
                                            options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
                                            st.session_state[unique_id] = options[max(0, min(5, res['score']))]
                                        st.rerun()

                            # Render Control
                            ai_data = st.session_state['ai_results'].get(unique_id)
                            score = ui.render_control_input(control, unique_id, ai_feedback=ai_data) # ui.render uses unique_id key in st.selectbox
                            st.session_state['responses'][unique_id] = score
                
                if not has_visible_controls:
                    st.warning(f"No visible controls for current wave.")

    # --- Render Sub-Tab Body ---
    tab_sel = st.session_state.get('assessment_tab_selection', 'Enterprise')
    
    if tab_sel == "Enterprise":
        st.session_state['scope_mode'] = 'Organization'
        render_assessment_view("org", "none", "Enterprise")
        
    elif tab_sel == "Cloud":
        st.session_state['scope_mode'] = 'Project'
        st.session_state['project_type_sel'] = 'Cloud'
        render_assessment_view("project", "cloud", "Solutions Cloud")

    elif tab_sel == "SaaS":
        st.session_state['scope_mode'] = 'Project' 
        st.session_state['project_type_sel'] = 'SaaS'
        render_assessment_view("project", "saas", "Solutions SaaS")


elif page == "Executive Dashboard":
    # Global Context Banner (for screenshots/presentations)  
    project_ctx = st.session_state.get('project_name', 'Organization')
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%); 
                    border-left: 4px solid #0EA5E9; 
                    padding: 8px 16px; 
                    margin-bottom: 12px; 
                    border-radius: 6px; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;">
            <span style="font-size: 0.85rem; color: #0C4A6E; font-weight: 600;">📊 {project_ctx} Executive View | Framework: NIST AI RMF + CSA AICM</span>
            <span style="font-size: 0.75rem; color: #0369A1;">Report Date: {datetime.date.today().strftime("%Y-%m-%d")}</span>
        </div>
    """, unsafe_allow_html=True)
    
    ui.display_header("Executive Security Dashboard", "Real-Time Governance & Maturity Analysis")
    
    # Auto-generated Executive Summary (placeholder, will be populated after metrics calculation)
    summary_placeholder = st.empty()
    
    df = storage.load_history()
    
    # Check if we have history, otherwise use Demo Data / Current Session
    # For MVP, let's allow "Current Session" visualization if no history
    has_history = not df.empty
    
    if has_history:
        # Selection Logic (Existing)
        col_sel, col_date = st.columns([3, 1])
        with col_sel:
            assessment_options = {}
            for index, row in df.iterrows():
                scope_label = row.get('scope', 'Org').upper() if row.get('scope') else 'ORG'
                ptype_label = f"({row.get('project_type')})" if row.get('project_type') and row.get('project_type') != 'none' else ""
                label = f"{row['project_name']} [{scope_label}{ptype_label}] ({row['timestamp']})"
                assessment_options[label] = row['id']
            selected_option = st.selectbox("Select Assessment Snapshot:", list(assessment_options.keys()))
            selected_id = assessment_options[selected_option]
        
        # Get data
        details_df = storage.get_assessment_details(selected_id)
        if not details_df.empty:
            # Reconstruct Category Scores
            category_scores = details_df.groupby('category')['score'].mean().to_dict()
            # Calculate Total Score
            sel_row = df[df['id'] == selected_id].iloc[0]
            
            with col_date:
                st.write("") # Spacer
                if st.button("📋 Clone as New Scenario", help="Load this snapshot to create a new version or modify responses", width='stretch'):
                    st.session_state['cloning_from'] = sel_row['project_name']
                    # Set Scope (Legacy, mostly for sidebar info)
                    sc = sel_row.get('scope', 'org')
                    pt = sel_row.get('project_type', 'none')

                    # Load Data - Fix Key Mismatch
                    st.session_state[f"proj_name_{sc}_{pt}"] = f"Copy of {sel_row['project_name']}"
                    
                    if sc.lower() == 'org': st.session_state['scope_mode'] = 'Organization'
                    else: 
                        st.session_state['scope_mode'] = 'Project'
                        st.session_state['project_type_sel'] = 'Cloud' if 'cloud' in pt.lower() else 'SaaS'
                    
                    # Populate Responses
                    new_responses = {}
                    for _, r in details_df.iterrows():
                        # Reconstruct Key: score_{scope}_{type}_{subcat}_{id}
                        subcat = mappings.get_subcat_from_id(r['question_id'])
                        if subcat != "Unmapped":
                             key = f"score_{sc}_{pt}_{subcat}_{r['question_id']}"
                             new_responses[key] = r['score']
                             
                             # Fix: Widget expects string from options list
                             options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
                             try:
                                 score_idx = max(0, min(5, int(r['score'])))
                                 st.session_state[key] = options[score_idx]
                             except:
                                 st.session_state[key] = options[0]
                             
                             # Restore AI/Notes if possible?
                             # Notes are in r['notes'], but AI widgets use separate keys.
                             # For MVP, restoring Scores is the critical part.
                    
                    st.session_state['responses'] = new_responses
                    target_tab = "Enterprise" if sc.lower() == 'org' else pt.title()
                    # Force the correct sub-tab to open
                    st.session_state['assessment_tab_selection'] = target_tab
                    
                    st.toast(f"Assessment Loaded! Opening '{target_tab}' assessment form.")
                    # Safe Navigation Switch
                    st.session_state['nav_override'] = "Assessment"
                    st.rerun()
            total_avg_score = sel_row['total_score']
            maturity_level = sel_row['maturity_level']
            # Mock Gaps count (Controls < 3)
            critical_gaps = details_df[details_df['score'] < 3].shape[0]
            compliance_pct = (details_df[details_df['score'] >= 3].shape[0] / details_df.shape[0]) * 100 if details_df.shape[0] > 0 else 0
            open_risks = critical_gaps  # Same as critical_gaps
            controls_implemented = details_df[details_df['score'] >= 3].shape[0]
            
    else:
        # DEMO / EMPTY STATE
        st.info("ℹ️ No historical snapshots found. Showing **Live Demo Simulation** of Executive View.")
        # Synthetic Data
        total_avg_score = 3.4
        maturity_level = "Managed"
        category_scores = {'GOVERN': 3.8, 'MAP': 3.2, 'MEASURE': 2.9, 'MANAGE': 3.5}
        critical_gaps = 12
        compliance_pct = 68
        open_risks = 12  # Demo: count of controls < 3
        controls_implemented = 92  # Demo: count of controls >= 3
        details_df = pd.DataFrame() # Initialize empty for safety
        
    # === ROI CONFIGURATION ===
    with st.expander("⚙️ ROI Assumptions (Click to Configure Financial Model)"):
        c_cost, c_prob = st.columns(2)
        with c_cost:
            breach_cost = st.number_input("Avg. Cost of Data Breach ($)", value=4450000, help="Source: IBM Cost of a Data Breach Report 2023")
        with c_prob:
            prob_rate = st.slider("Baseline Incident Probability (Annual)", 0.0, 1.0, 0.35, help="Probability of a significant AI incident without controls (Level 1)")

    # Calculate ROI based on score
    roi_results = roi.calculate_roi(total_avg_score, baseline_breach_cost=breach_cost, prob_low_maturity=prob_rate)
    
    # Generate Executive Summary
    if total_avg_score >= 4.5:
        summary_text = f"Organization is operating at **{maturity_level}** security maturity with no critical gaps identified. Estimated annual risk reduction: **${roi_results['estimated_savings']/1000000:.1f}M**."
    elif total_avg_score >= 3.0:
        summary_text = f"Organization is at **{maturity_level}** maturity with **{critical_gaps}** areas requiring attention. Current risk posture shows **{roi_results['reduction_pct']:.0f}%** improvement over baseline."
    else:
        summary_text = f"Organization is at **{maturity_level}** maturity with **{critical_gaps}** critical gaps. Immediate action recommended to reduce **${roi_results['current_exposure']/1000000:.1f}M** annual loss exposure."
    
    summary_placeholder.info(f"📊 **Executive Summary**: {summary_text}")
    
    # === ROW 1: HEADLINE METRICS ===
    # Gauge + 3 KPI Cards
    col_gauge, col_kpi = st.columns([1.5, 2.5])
    
    with col_gauge:
        st.markdown('<div class="glass-card" style="height: 100%; display: flex; align-items: center; justify-content: center;">', unsafe_allow_html=True)
        fig_gauge = charts.plot_gauge_chart(total_avg_score)
        st.plotly_chart(fig_gauge, width='stretch', config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_kpi:
        # 4 KPI Cards Layout
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-top: 4px solid #10B981 !important;">
                    <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Maturity Level</p>
                    <h2 style="color: #10B981; font-size: 1.8rem; margin: 10px 0;">{maturity_level}</h2>
                    <p style="color: #64748B; font-size: 0.8rem;">Current Status</p>
                </div>
            """, unsafe_allow_html=True)
            
        with kpi_col2:
             st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-top: 4px solid #EF4444 !important;">
                    <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Open Risks</p>
                    <h2 style="color: #EF4444; font-size: 1.8rem; margin: 10px 0;">{open_risks}</h2>
                    <p style="color: #64748B; font-size: 0.8rem;">To Remediate</p>
                </div>
            """, unsafe_allow_html=True)
            
        with kpi_col3:
             st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-top: 4px solid #3B82F6 !important;">
                    <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Compliance</p>
                    <h2 style="color: #3B82F6; font-size: 1.8rem; margin: 10px 0;">{compliance_pct:.0f}%</h2>
                    <p style="color: #64748B; font-size: 0.8rem;">NIST Aligned</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi_col4:
            st.markdown(f"""
                <div class="glass-card" style="text-align: center; border-top: 4px solid #3B82F6 !important;">
                    <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Financial Risk Reduction</p>
                    <h2 style="color: #3B82F6; font-size: 1.5rem; margin: 10px 0;">${roi_results['estimated_savings']/1000000:.1f}M</h2>
                    <p style="color: #3B82F6; font-size: 0.8rem; font-weight: 600;">ALE Reduction</p>
                </div>
            """, unsafe_allow_html=True)
            
    # === ROW 2: DETAILED ANALYSIS ===
    col_radar, col_bench = st.columns([1, 1])
    
    with col_radar:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🕸️ NIST AI RMF Profile")
        fig_radar = charts.plot_radar_chart(list(category_scores.keys()), list(category_scores.values()))
        st.plotly_chart(fig_radar, width='stretch', config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_bench:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Industry Benchmark")
        fig_bench = charts.plot_benchmark_chart(category_scores)
        st.plotly_chart(fig_bench, width='stretch', config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # === ROW 3: RISK MATRIX ===
    st.subheader("🎯 Priority Risk Matrix")
    fig_risk = charts.plot_risk_heatmap(details_df)
    if fig_risk:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_risk, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("✅ No critical gaps identified! Risk exposure is minimal.")

    st.subheader("🚀 Recommended Actions (Strategic Roadmap)")
    st.markdown("""
    <div class="glass-card">
        <table style="width:100%; border-collapse: collapse;">
            <tr style="border-bottom: 2px solid #E2E8F0;">
                <th style="text-align: left; padding: 12px; color: #475569;">Priority</th>
                <th style="text-align: left; padding: 12px; color: #475569;">Action Item</th>
                <th style="text-align: left; padding: 12px; color: #475569;">Impact</th>
                <th style="text-align: left; padding: 12px; color: #475569;">Est. Effort</th>
            </tr>
            <tr style="border-bottom: 1px solid #F1F5F9;">
                <td style="padding: 12px;"><span style="background: #FEE2E2; color: #991B1B; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">High</span></td>
                <td style="padding: 12px; color: #1E293B; font-weight: 500;">Implement Model Inventory Tracking (MAP 1.1)</td>
                <td style="padding: 12px; color: #334155;">Critical Risk Reduction</td>
                <td style="padding: 12px; color: #334155;">2 Weeks</td>
            </tr>
            <tr style="border-bottom: 1px solid #F1F5F9;">
                <td style="padding: 12px;"><span style="background: #FEE2E2; color: #991B1B; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">High</span></td>
                <td style="padding: 12px; color: #1E293B; font-weight: 500;">Define AI Acceptable Use Policy (GOVERN 2.3)</td>
                <td style="padding: 12px; color: #334155;">Governance Baseline</td>
                <td style="padding: 12px; color: #334155;">1 Week</td>
            </tr>
            <tr>
                <td style="padding: 12px;"><span style="background: #FEF3C7; color: #92400E; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">Medium</span></td>
                <td style="padding: 12px; color: #1E293B; font-weight: 500;">Automate Drift Detection (MEASURE 2.1)</td>
                <td style="padding: 12px; color: #334155;">Operational Stability</td>
                <td style="padding: 12px; color: #334155;">1 Month</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # === REPORT GENERATION ===
    if 'fig_gauge' in locals() and 'fig_radar' in locals():
        st.markdown("### 📄 Executive Reporting")
        col_rep_btn, col_rep_info = st.columns([1, 3])
        
        with col_rep_btn:
            # Prepare Data
            metrics = {
                'score': total_avg_score,
                'maturity': maturity_level,
                'gaps': critical_gaps,
                'compliance': compliance_pct,
                'savings': roi_results.get('estimated_savings', 0)
            }
            charts_dict = {
                'gauge': fig_gauge,
                'radar': fig_radar,
                'benchmark': fig_bench if 'fig_bench' in locals() else None,
                'risk': fig_risk if 'fig_risk' in locals() else None
            }
            meta = {
                'org': st.session_state.get('project_name', 'My Organization'),
                'date': sel_row['timestamp'] if 'sel_row' in locals() else datetime.date.today().strftime("%Y-%m-%d"),
                'scope': st.session_state.get('scope_mode', 'Organization')
            }
            
            # Generate HTML
            # Lazy load: only generate when needed? No, Streamlit needs data for btn.
            # Efficient enough for local execution.
            if 'details_df' not in locals(): details_df = pd.DataFrame() # Handle empty
            html_report = reporting.generate_html_report(metrics, charts_dict, details_df, meta)
            
            st.download_button(
                label="📥 Download PDF Report (Printable)",
                data=html_report,
                file_name=f"executive_report_{meta['date']}.html",
                mime="text/html",
                help="Generates an enterprise-ready report including Maturity Gauge, Benchmarks, and NIST/CSA Mapping."
            )
            st.markdown('<p style="color: #64748B; font-size: 0.8rem; margin-top: -10px;">Contains detailed control mapping to NIST AI RMF & CSA AICM</p>', unsafe_allow_html=True)
        with col_rep_info:
             st.info("💡 **Pro Tip:** For a vector-quality Board Report, open the downloaded file and use **Print to PDF**.")

    # === ROW 4: DETAILED AUDIT & COMPLIANCE LOG ===
    if 'details_df' in locals() and not details_df.empty:
        st.markdown("---")
        with st.expander("🔍 View Detailed Assessment & Compliance Matrix", expanded=False):
            st.info(f"Showing detailed records for: **{selected_option if 'selected_option' in locals() else 'Detailed View'}**")
            
            # Prepare DataFrame for Display
            display_df = details_df.copy()
            
            # --- COMPLIANCE MAPPING ---
            # 1. Get NIST Subcategory (e.g. GOVERN 1.1)
            display_df['nist_subcat'] = display_df['question_id'].apply(mappings.get_subcat_from_id)
            
            # 2. Get Requirement Text
            display_df['Requirement'] = display_df['question_id'].apply(lambda x: mappings.get_control_info(x)['text'])
            
            # 3. Get Framework Mappings
            def get_map(subcat, framework):
                m = mappings.get_compliance_mapping(subcat)
                return m.get(framework, '-')
                
            display_df['NIST GenAI (600-1)'] = display_df['nist_subcat'].apply(lambda x: get_map(x, 'nist_600_1'))
            display_df['ISO 27001'] = display_df['nist_subcat'].apply(lambda x: get_map(x, 'iso_27001'))
            display_df['EU AI Act'] = display_df['nist_subcat'].apply(lambda x: get_map(x, 'eu_ai_act'))
            
            # Safely filter columns
            cols_to_show = ['category', 'question_id', 'Requirement', 'score', 'notes', 'NIST GenAI (600-1)', 'ISO 27001', 'EU AI Act']
            available_cols = [c for c in cols_to_show if c in display_df.columns]
            display_df = display_df[available_cols]
            
            # Rename for users
            col_map = {
                'category': 'Function',
                'question_id': 'ID',
                'score': 'Score',
                'notes': 'Justification/Notes'
            }
            display_df = display_df.rename(columns=col_map)
            
            # Style
            def color_score(val):
                color = '#EF4444' if (isinstance(val, (int, float)) and val < 3) else '#10B981'
                return f'color: {color}; font-weight: bold'
                
            st.dataframe(
                display_df.style.map(color_score, subset=['Score']) if 'Score' in display_df.columns else display_df,
                width='stretch',
                column_config={
                    "Score": st.column_config.NumberColumn(
                        "Maturity (0-5)",
                        help="Score 0 to 5",
                        format="%d ⭐"
                    ),
                    "Requirement": st.column_config.TextColumn("Control Requirement", width="large"),
                    "Justification/Notes": st.column_config.TextColumn("Justification", width="medium"),
                    "NIST GenAI (600-1)": st.column_config.TextColumn("NIST 600-1 (GenAI)", width="medium"),
                    "ISO 27001": st.column_config.TextColumn("ISO 27001 Mapping", width="small")
                }
            )
            
            # Export Button
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Compliance CSV",
                data=csv,
                file_name=f"compliance_matrix_{selected_id if 'selected_id' in locals() else 'snapshot'}.csv",
                mime="text/csv",
            )

elif page == "Evidence Locker":
    ui.display_header("Evidence Locker", "Manage your uploaded documents")
    
    # File uploader
    uploaded_files = st.file_uploader("Upload evidence documents (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Save the file
            file_path = evidence.save_evidence_file(uploaded_file)
            st.success(f"Uploaded: {uploaded_file.name}")
    
    st.markdown("---")
    st.subheader("Current Evidence Files")
    
    files = evidence.list_evidence_files()
    if not files:
        st.info("No evidence files uploaded yet.")
    else:
        for f in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"📄 {f}")
            with col2:
                if st.button("Delete", key=f"delete_{f}"):
                    evidence.delete_evidence_file(f)
                    st.success(f"Deleted {f}")
                    st.rerun()
