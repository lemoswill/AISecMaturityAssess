__import__('pysqlite3')
import sys
import os
import shutil
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import pandas as pd
from modules import data, storage, ui, charts, evidence, ai_engine

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

# Handle programmatic navigation
if 'navigate_to' in st.session_state:
    page = st.session_state['navigate_to']
    del st.session_state['navigate_to']
else:
    # Custom styled radio buttons
    page = st.sidebar.radio(
        "nav_label",
        ["Assessment", "History & Dashboard", "Evidence Locker"],
        label_visibility="collapsed"
    )

st.sidebar.markdown("---")

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
    <p style="color: #92400E; font-size: 0.75rem; font-weight: 800; margin: 0 0 6px 0;">🧪 DEMO MODE</p>
    <p style="color: #78350F; font-size: 0.8rem; margin: 0; line-height: 1.5; font-weight: 500;">
        Data is <strong>not persisted</strong> between sessions.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Style & Appearance ---
st.sidebar.markdown('<p style="color: #64748B; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem;">Appearance Settings</p>', unsafe_allow_html=True)

theme_choice = st.sidebar.radio(
    "Select Interface Style",
    ["Silicon Precision", "Palo Alto Enterprise"],
    index=0 if st.session_state['ui_style'] == "Silicon Precision" else 1,
    help="Toggle between professional Glassmorphism and Palo Alto Enterprise design.",
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
    
    uploaded_files = st.file_uploader("Drop PDF/Text files here", type=['pdf', 'txt', 'md'], accept_multiple_files=True, label_visibility="collapsed")
    
    if uploaded_files:
        if st.button(f"⚡ Index {len(uploaded_files)} Resources", type="primary"):
            with st.spinner("Processing Intelligence..."):
                engine = ai_engine.get_engine()
                for up_file in uploaded_files:
                    saved_path = evidence.save_uploaded_file(up_file)
                    if saved_path:
                        success, _ = engine.ingest_file(up_file.name)
            st.success("Indexing Complete!")
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # 3. View Index
    st.markdown("### 📚 Intelligence Assets")
    files = evidence.list_evidence_files()
    if files:
        for f in files:
            st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 15px; border-radius: 10px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
                    <span style="color: #334155; font-size: 0.9rem; font-weight: 500;">{f}</span>
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

    scope_tabs = st.tabs(["🏛️ Enterprise", "☁️ Solutions Cloud", "📦 Solutions SaaS"])
    
    current_scope = "org"
    current_type = "none"
    
    # We will determine scope/type based on which tab is rendered.
    # Note: Streamlit executes ALL tabs. Use a unified render function or logic block.
    # To avoid triple-executing heavy logic, we can define the active context *before* rendering,
    # but st.tabs returns containers. We must put content *inside* the tab context.
    
    selected_tab_idx = 0 
    # Logic: We can't easily know 'which tab is active' in Python without a separate variable or component.
    # However, standard `with tab:` Just Works™ for layout.
    # We will wrap the core assessment rendering in a function.
    
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
                    format_func=lambda x: f"{x} - {data.NIST_FUNCTIONS[x]}",
                    label_visibility="collapsed"
                )
            
            with col_act:
                current_provider = st.session_state.get('ai_provider', 'OpenAI')
                provider_keys = st.session_state.get('provider_keys', {})
                active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
                
                if active_key:
                    if st.button(f"🚀 Analyze {selected_domain}", key=f"btn_analyze_{scope_key}_{type_key}", type="primary", use_container_width=True):
                        st.session_state['trigger_bulk_assess'] = selected_domain
                        st.session_state['active_tab_context'] = (scope_key, type_key) # Track where we came from
                        st.rerun()
                else:
                    st.button("🔑 Key Required", key=f"btn_lock_{scope_key}_{type_key}", type="secondary", use_container_width=True, disabled=True)
        
        st.markdown("---")
    
        # --- Maturity Journey (Phase Tracker) ---
        st.markdown("""<h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
            Maturity Journey Phase
        </h3>""", unsafe_allow_html=True)
        
        wave_names = list(data.MATURITY_WAVES.values())
        wave_options = ["All Waves"] + wave_names
        
        # Load CSS (already loaded globally, but ensuring scope)
        
        col_wave, _ = st.columns([1, 2])
        with col_wave:
            selected_wave_label = st.selectbox(
                "Current Phase",
                wave_options,
                index=1,
                key=f"wave_sel_{scope_key}_{type_key}",
                label_visibility="collapsed"
            )
        
        # Local wave filter logic
        if selected_wave_label == "All Waves":
            selected_wave_id = None
        else:
            selected_wave_id = next(k for k, v in data.MATURITY_WAVES.items() if v == selected_wave_label)
        
        # --- Project Name & Progress Indicator ---
        col_name, col_progress = st.columns([2, 1])
        
        with col_name:
            project_name = st.text_input("Project / Product Name", placeholder="e.g. Finance Chatbot v2", key=f"proj_name_{scope_key}_{type_key}")
        
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
                label=f"Progress ({selected_wave_label})", 
                value=f"{completed_controls}/{total_controls}", 
                delta=f"{completion_pct:.0f}%",
                delta_color="normal"
            )
        
        # --- Save & Download Button ---
        if st.button("💾 Save & Download Report", key=f"save_btn_{scope_key}_{type_key}", type="primary", use_container_width=True):
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
                
                import io
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
                st.markdown(f"### {func}: {data.NIST_FUNCTIONS.get(func, '')}")
                
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
                    
                    # Subcat Header
                    current_subcat_total = 0
                    for c in visible_controls:
                        unique_id = f"score_{scope_key}_{type_key}_{subcat_key}_{c['id']}"
                        val = st.session_state.get(unique_id, 0)
                        score = 0
                        if isinstance(val, int): score = val
                        elif isinstance(val, str):
                            try: score = int(val.split('(')[-1].strip(')'))
                            except: pass
                        current_subcat_total += score
                    subcat_avg = current_subcat_total / len(visible_controls) if visible_controls else 0
                    
                    with st.expander(f"{subcat_key}"):
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

    # --- Render Tabs ---
    with scope_tabs[0]:
        st.session_state['scope_mode'] = 'Organization' # Sync for other components
        render_assessment_view("org", "none", "Enterprise")
        
    with scope_tabs[1]:
        st.session_state['scope_mode'] = 'Project'
        st.session_state['project_type_sel'] = 'Cloud'
        render_assessment_view("project", "cloud", "Solutions Cloud")

    with scope_tabs[2]:
        st.session_state['scope_mode'] = 'Project' 
        st.session_state['project_type_sel'] = 'SaaS'
        render_assessment_view("project", "saas", "Solutions SaaS")


elif page == "History & Dashboard":
    ui.display_header("Assessment Dashboard", "Historical analysis and visualizations")
    
    df = storage.load_history()
    
    if df.empty:
        st.info("No assessments found.")
    else:
        # Selection Logic
        assessment_options = {}
        for index, row in df.iterrows():
            scope_label = row.get('scope', 'Org').upper() if row.get('scope') else 'ORG'
            ptype_label = f"({row.get('project_type')})" if row.get('project_type') and row.get('project_type') != 'none' else ""
            label = f"{row['project_name']} [{scope_label}{ptype_label}] ({row['timestamp']})"
            assessment_options[label] = row['id']
        selected_option = st.selectbox("Select Assessment to View:", list(assessment_options.keys()))
        selected_id = assessment_options[selected_option]
        
        # Get details
        details_df = storage.get_assessment_details(selected_id)
        
        if not details_df.empty:
            # Reconstruct Scores
            # Group by 'category' (NIST Function) and take average of 'score'
            # Note: This is an approximation. Ideally we'd replicate the exact Rollup logic (Avg of Subcats),
            # but since we stored 'category' as the Function name, Avg(Controls) is a close proxy for Avg(Function) if subcats are balanced.
            # To be precise, we should have stored Subcat info more explicitly.
            # For now, Avg(Controls per Function) is acceptable for the View.
            
            category_scores = details_df.groupby('category')['score'].mean().to_dict()
            
            # Overview Metrics (Glass Cards)
            sel_row = df[df['id'] == selected_id].iloc[0]
            
            st.markdown(f"""
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem;">
                    <div class="glass-card" style="margin-bottom: 0;">
                        <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 10px 0;">Project Name</p>
                        <h2 style="color: #0F172A; margin: 0; font-size: 1.5rem;">{sel_row['project_name']}</h2>
                    </div>
                    <div class="glass-card" style="margin-bottom: 0; border-left: 5px solid #2563EB !important;">
                        <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 10px 0;">Total Maturity</p>
                        <h2 style="color: #2563EB; margin: 0; font-size: 1.5rem;">{sel_row['total_score']:.2f} <span style="font-size: 0.9rem; color: #94A3B8;">/ 5.0</span></h2>
                    </div>
                    <div class="glass-card" style="margin-bottom: 0; border-left: 5px solid #10B981 !important;">
                        <p style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 10px 0;">Maturity Level</p>
                        <h2 style="color: #10B981; margin: 0; font-size: 1.5rem;">{sel_row['maturity_level']}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Charts
            col_chart1, col_chart2 = st.columns([1, 1])
            
            with col_chart1:
                st.subheader("Maturity Profile (NIST AI RMF)")
                # Ensure all categories are present even if 0
                final_cat_scores = []
                final_cat_names = list(data.NIST_FUNCTIONS.keys())
                for cat in final_cat_names:
                    final_cat_scores.append(category_scores.get(cat, 0))
                    
                charts.plot_radar_chart(final_cat_names, final_cat_scores)
                
            with col_chart2:
                st.subheader("Detailed Breakdown")
                st.dataframe(details_df[['category', 'question_id', 'score']].style.background_gradient(cmap='Blues'), use_container_width=True)
