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
ui.load_custom_css()

# --- Session State ---
if 'responses' not in st.session_state:
    st.session_state['responses'] = {}
if 'ai_results' not in st.session_state:
    st.session_state['ai_results'] = {}

# --- Sidebar ---
st.sidebar.markdown("""
<div style="text-align: center; padding: 2rem 0 1.5rem 0; border-bottom: 1px solid #F1F5F9; margin-bottom: 2rem;">
    <div style="background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%); 
                width: 60px; height: 60px; border-radius: 16px; 
                display: flex; align-items: center; justify-content: center; 
                margin: 0 auto 16px auto; 
                box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z" 
                  stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="white" fill-opacity="0.2"/>
            <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <h1 style="color: #0F172A; margin: 0; font-size: 1.1rem; font-weight: 800; letter-spacing: -0.01em;">AI Security</h1>
    <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Silicon Precision Edition</p>
</div>
""", unsafe_allow_html=True)

# Navigation Section
st.sidebar.markdown("""
<style>
    /* Custom Radio Button Styling */
    div[data-testid="stSidebar"] .stRadio > label {
        background: transparent;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid transparent;
    }
    
    div[data-testid="stSidebar"] .stRadio > label:hover {
        background: #F8FAFC;
        border-color: #E2E8F0;
    }
    
    div[data-testid="stSidebar"] .stRadio > label[data-checked="true"] {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid #0066CC;
        font-weight: 600;
        color: #1E3A8A;
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
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #0066CC;
            margin-bottom: 1rem;">
    <p style="color: #1E3A8A; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 8px 0;">Architecture</p>
    <p style="color: #1E40AF; font-size: 0.85rem; margin: 0; line-height: 1.6;">
        <strong>Macro:</strong> NIST AI RMF<br>
        <strong>Detail:</strong> CSA AICM Controls
    </p>
</div>
""", unsafe_allow_html=True)

# Demo Warning Banner
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #F59E0B;
            margin-bottom: 1rem;">
    <p style="color: #92400E; font-size: 0.75rem; font-weight: 700; margin: 0 0 6px 0;">🧪 DEMO MODE</p>
    <p style="color: #78350F; font-size: 0.75rem; margin: 0; line-height: 1.5;">
        Data is <strong>not persisted</strong> between sessions.
    </p>
    <p style="color: #059669; font-size: 0.75rem; margin: 8px 0 0 0; font-weight: 600;">
        ✅ Download your assessment before closing!
    </p>
</div>
""", unsafe_allow_html=True)

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
    
    # --- Silicon Precision Hero Section ---
    st.markdown("""
    <div class="glass-card" style="padding: 2.5rem; margin-top: 1rem; border-left: 8px solid #2563EB !important;">
        <div style="display: flex; align-items: center; gap: 24px;">
            <div style="background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%); 
                        padding: 18px; 
                        border-radius: 14px;
                        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z" 
                          stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="white" fill-opacity="0.15"/>
                    <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div style="flex: 1;">
                <h1 style="color: #0F172A; margin: 0; font-size: 1.8rem;">AI Security Maturity</h1>
                <p style="color: #64748B; margin: 4px 0 0 0; font-size: 1rem; font-weight: 500;">
                    Governance & Engineering Platform • <span style="color: #2563EB;">Silicon Precision Edition</span>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Smart CTA Logic ---
    files = evidence.list_evidence_files()
    has_evidence = len(files) > 0
    
    if not has_evidence:
        st.warning("⚠️ **No evidence uploaded yet.** Please upload your security documentation in the Evidence Locker to enable AI assessment.")
    else:
        st.success(f"✅ **Intelligence Engine Online** - {len(files)} document(s) indexed")
        
        # --- AI Command Center Trigger ---
        available_domains = list(data.NIST_FUNCTIONS.keys())
        
        col_dom, col_act = st.columns([3, 1])
        with col_dom:
            selected_domain = st.selectbox(
                "Choose NIST Function to Analyze",
                available_domains,
                format_func=lambda x: f"{x} - {data.NIST_FUNCTIONS[x]}",
                label_visibility="collapsed"
            )
        
        with col_act:
            current_provider = st.session_state.get('ai_provider', 'OpenAI')
            provider_keys = st.session_state.get('provider_keys', {})
            active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
            
            if active_key:
                if st.button(f"🚀 Analyze {selected_domain}", type="primary", use_container_width=True):
                    st.session_state['trigger_bulk_assess'] = selected_domain
                    st.rerun()
            else:
                st.button("🔑 Key Required", type="secondary", use_container_width=True, disabled=True)
    
    st.markdown("---")

    # --- Maturity Journey (Phase Tracker) ---
    st.markdown("""<h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
        Maturity Journey Phase
    </h3>""", unsafe_allow_html=True)
    
    wave_names = list(data.MATURITY_WAVES.values())
    wave_options = ["All Waves"] + wave_names
    
    # Custom CSS for the Phase Tracker
    st.markdown("""
        <style>
            .phase-tracker {
                display: flex;
                justify-content: space-between;
                margin-bottom: 2rem;
                position: relative;
                padding: 0 10px;
            }
            .phase-tracker::before {
                content: '';
                position: absolute;
                top: 15px;
                left: 5%;
                right: 5%;
                height: 2px;
                background: #E2E8F0;
                z-index: 1;
            }
            .phase-step {
                position: relative;
                z-index: 2;
                background: #F8FAFC;
                padding: 0 10px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .phase-node {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: #FFFFFF;
                border: 2px solid #E2E8F0;
                margin: 0 auto 8px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.8rem;
                font-weight: 700;
                color: #94A3B8;
                transition: all 0.3s ease;
            }
            .phase-active .phase-node {
                background: #2563EB;
                border-color: #2563EB;
                color: #FFFFFF;
                box-shadow: 0 0 12px rgba(37, 99, 235, 0.4);
            }
            .phase-active .phase-label {
                color: #2563EB;
                font-weight: 700;
            }
            .phase-label {
                font-size: 0.8rem;
                color: #64748B;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

    # Use a native selectbox for functionality but style it as a phase tracker? 
    # Or just use the selectbox styled nicely. Let's stick to a clean selectbox for now but place it prominently.
    
    col_wave, _ = st.columns([1, 2])
    with col_wave:
        selected_wave_label = st.selectbox(
            "Current Phase",
            wave_options,
            index=1, # Default to Wave 1
            label_visibility="collapsed"
        )
    
    st.session_state['wave_filter'] = selected_wave_label
    
    if selected_wave_label == "All Waves":
        selected_wave_id = None
    else:
        selected_wave_id = next(k for k, v in data.MATURITY_WAVES.items() if v == selected_wave_label)
    
    # --- Project Name & Progress Indicator ---
    col_name, col_progress = st.columns([2, 1])
    
    with col_name:
        project_name = st.text_input("Project / Product Name", placeholder="e.g. Finance Chatbot v2")
    
    with col_progress:
        # Calculate completion (respecting wave filter)
        # Note: selected_wave_id is defined later, so we need to calculate it here first
        wave_options_temp = ["All Waves"] + list(data.MATURITY_WAVES.values())
        selected_wave_label_temp = st.session_state.get('wave_filter', wave_options_temp[1])
        
        if selected_wave_label_temp == "All Waves":
            selected_wave_id_temp = None
        else:
            selected_wave_id_temp = next((k for k, v in data.MATURITY_WAVES.items() if v == selected_wave_label_temp), 1)
        
        total_controls = 0
        completed_controls = 0
        
        for func in data.ASSESSMENT_DATA:
            for subcat_key in data.ASSESSMENT_DATA[func]:
                for control in data.ASSESSMENT_DATA[func][subcat_key]['csa_controls']:
                    # Filter by wave
                    if selected_wave_id_temp is not None and control.get('wave', 2) != selected_wave_id_temp:
                        continue
                    
                    total_controls += 1
                    unique_id = f"score_{subcat_key}_{control['id']}"
                    val = st.session_state.get(unique_id, 0)
                    
                    # Check if scored (not 0)
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
        
        # Display Progress + Wave Label
        st.metric(
            label=f"Progress ({selected_wave_label_temp})", 
            value=f"{completed_controls}/{total_controls}", 
            delta=f"{completion_pct:.0f}%",
            delta_color="normal"
        )
    
    # --- Save & Download Button ---
    if st.button("💾 Save & Download Report", type="primary", use_container_width=True):
        if not project_name:
            st.error("⚠️ Please enter a project name before saving.")
        else:
            # Prepare responses
            final_responses = []
            for func in data.ASSESSMENT_DATA:
                for subcat_key in data.ASSESSMENT_DATA[func]:
                    for control in data.ASSESSMENT_DATA[func][subcat_key]['csa_controls']:
                        unique_id = f"score_{subcat_key}_{control['id']}"
                        val = st.session_state.get(unique_id, 0)
                        
                        # Parse score
                        score = 0
                        if isinstance(val, int):
                            score = val
                        elif isinstance(val, str) and "(" in val:
                            try:
                                score = int(val.split('(')[-1].strip(')'))
                            except:
                                score = 0
                        
                        # AI Analysis data
                        ai_data = st.session_state.get('ai_results', {}).get(unique_id, {})
                        ai_justification = ai_data.get('justification', '')
                        ai_sources = ", ".join(ai_data.get('sources', [])) if ai_data.get('sources') else ''

                        final_responses.append({
                            "category": func,
                            "question_id": control['id'],
                            "score": score,
                            "ai_justification": ai_justification,
                            "ai_sources": ai_sources,
                            "mapping": subcat_key
                        })
            
            # Calculate stats
            func_scores = {}
            for func in data.ASSESSMENT_DATA:
                func_total = 0
                func_count = 0
                for subcat_key in data.ASSESSMENT_DATA[func]:
                    for control in data.ASSESSMENT_DATA[func][subcat_key]['csa_controls']:
                        unique_id = f"score_{subcat_key}_{control['id']}"
                        val = st.session_state.get(unique_id, 0)
                        
                        score = 0
                        if isinstance(val, int):
                            score = val
                        elif isinstance(val, str) and "(" in val:
                            try:
                                score = int(val.split('(')[-1].strip(')'))
                            except:
                                pass
                        
                        func_total += score
                        func_count += 1
                
                func_scores[func] = func_total / func_count if func_count > 0 else 0
            
            avg_score = sum(func_scores.values()) / len(func_scores) if func_scores else 0
            
            # Determine level
            level = "Initial"
            if avg_score > 1.5: level = "Defined"
            if avg_score > 3.0: level = "Managed"
            if avg_score > 4.5: level = "Optimized"
            
            # Save to DB
            storage.save_assessment(project_name, final_responses, avg_score, level)
            
            # Generate CSV
            import io
            csv_buffer = io.StringIO()
            df_export = pd.DataFrame(final_responses)
            df_export.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.success(f"✅ Assessment saved for **{project_name}**!")
            st.download_button(
                label="📥 Download CSV Report",
                data=csv_data,
                file_name=f"{project_name.replace(' ', '_')}_assessment.csv",
                mime="text/csv",
                type="secondary"
            )
            st.balloons()
    
    st.markdown("---")
    
    project_name = st.text_input("Project / Product Name", placeholder="e.g. Finance Chatbot v2", key="project_name_hidden", label_visibility="collapsed")
    
    # Scoring Roll-up Logic
    nist_function_scores = {}
    
    # Display wave info
    if selected_wave_label == "All Waves":
        st.info(f"Viewing **All Waves** (Complete Assessment)")
    else:
        st.info(f"🌊 Viewing **{selected_wave_label}**. Focus on these requirements first.")
        
    # --- Handle Triggered Bulk Assessment from Hero ---
    if 'trigger_bulk_assess' in st.session_state:
        target_func = st.session_state['trigger_bulk_assess']
        del st.session_state['trigger_bulk_assess']
        
        st.info(f"🤖 Starting AI analysis for **{target_func}**...")
        
        # Get provider info
        current_provider = st.session_state.get('ai_provider', 'OpenAI')
        provider_keys = st.session_state.get('provider_keys', {})
        active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
        
        if active_key:
            # Gather controls for this function
            target_controls = []
            subcats_bulk = data.ASSESSMENT_DATA[target_func]
            for sk, sd in subcats_bulk.items():
                c_list = sd.get('csa_controls', [])
                if selected_wave_id is not None:
                    target_controls.extend([(sk, c) for c in c_list if c.get('wave', 2) == selected_wave_id])
                else:
                    target_controls.extend([(sk, c) for c in c_list])
            
            if target_controls:
                progress_bar = st.progress(0)
                status_text = st.empty()
                engine = ai_engine.get_engine()
                
                for idx, (sk, c) in enumerate(target_controls):
                    status_text.text(f"Analyzing {idx+1}/{len(target_controls)}: {c['id']}...")
                    progress_bar.progress((idx + 1) / len(target_controls))
                    
                    unique_id = f"score_{sk}_{c['id']}"
                    
                    try:
                        res = engine.assess_control(
                            c['text'], 
                            c.get('help', ''), 
                            active_key,
                            provider=current_provider
                        )
                        st.session_state['ai_results'][unique_id] = res
                        if 'score' in res and isinstance(res['score'], int):
                            st.session_state['responses'][unique_id] = res['score']
                            options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
                            safe_idx = max(0, min(5, res['score']))
                            st.session_state[unique_id] = options[safe_idx]
                    except Exception as e:
                        print(f"Error: {e}")
                
                status_text.text(f"✅ {target_func} analysis complete!")
                progress_bar.empty()
                st.success(f"Analyzed {len(target_controls)} controls in {target_func}")
                st.balloons()
        
    tabs = st.tabs(list(data.ASSESSMENT_DATA.keys()))
    
    for i, func in enumerate(data.ASSESSMENT_DATA):
        with tabs[i]:
            st.markdown(f"### {func}: {data.NIST_FUNCTIONS.get(func, '')}")
            
            # --- Bulk Auto-Assess ---
            current_provider = st.session_state.get('ai_provider', 'OpenAI')
            provider_keys = st.session_state.get('provider_keys', {})
            active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
            
            if active_key:
                 st.markdown(f"""
                 <div style="background: rgba(37, 99, 235, 0.05); border: 1px dashed rgba(37, 99, 235, 0.3); border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem;">
                     <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.5"><path d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        <strong style="color: #1E293B;">AI Command Center</strong>
                     </div>
                     <p style="font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;">Analyze all visible requirements in this domain using {current_provider}.</p>
                 </div>
                 """, unsafe_allow_html=True)
                 
                 if st.button(f"✨ Auto-Assess All ({func})", key=f"bulk_{func}", type="primary"):
                    
                    # Gather controls
                    target_controls = []
                    subcats_bulk = data.ASSESSMENT_DATA[func]
                    for sk, sd in subcats_bulk.items():
                        c_list = sd.get('csa_controls', [])
                        if selected_wave_id is not None:
                            target_controls.extend([c for c in c_list if c.get('wave', 2) == selected_wave_id])
                        else:
                            target_controls.extend(c_list)
                            
                    if not target_controls:
                         st.warning("No controls visible to assess.")
                    else:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        engine = ai_engine.get_engine()
                        provider_models = st.session_state.get('provider_models', {})
                        active_model = provider_models.get(current_provider)
                        
                        count = 0
                        for sk, sd in subcats_bulk.items():
                            c_list = sd.get('csa_controls', [])
                            valid_c = [c for c in c_list if (selected_wave_id is None) or (c.get('wave', 2) == selected_wave_id)]
                            
                            for c in valid_c:
                                count += 1
                                status_text.markdown(f"<span class='mono-text'>[{count}/{len(target_controls)}] Analyzing: {c['id']}</span>", unsafe_allow_html=True)
                                progress_bar.progress(count / len(target_controls))
                                
                                unique_id = f"score_{sk}_{c['id']}"
                                
                                try:
                                    res = engine.assess_control(c['text'], c.get('help', ''), active_key, provider=current_provider, model_name=active_model)
                                    st.session_state['ai_results'][unique_id] = res
                                    if 'score' in res and isinstance(res['score'], int):
                                        st.session_state['responses'][unique_id] = res['score']
                                        options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
                                        st.session_state[unique_id] = options[max(0, min(5, res['score']))]
                                except Exception as e:
                                    print(f"Error assessing {c['id']}: {e}")
                                    
                        status_text.success("✅ Analysis Complete!")
                        progress_bar.empty()
                        st.rerun()
            
            st.divider()

            subcats = data.ASSESSMENT_DATA[func]
            function_total_score = 0
            has_visible_controls = False
            
            for subcat_key, subcat_data in subcats.items():
                csa_controls = subcat_data.get('csa_controls', [])
                
                # Filter Controls by Wave
                if selected_wave_id is not None:
                    visible_controls = [c for c in csa_controls if c.get('wave', 2) == selected_wave_id]
                else:
                    visible_controls = csa_controls
                    
                if not visible_controls:
                    continue
                    
                has_visible_controls = True
                
                # Calculate subcat avg score
                current_subcat_total = 0
                for c in visible_controls:
                    unique_id = f"score_{subcat_key}_{c['id']}"
                    val = st.session_state.get(unique_id, 0)
                    score = 0
                    if isinstance(val, int): score = val
                    elif isinstance(val, str):
                        try: score = int(val.split('(')[-1].strip(')'))
                        except: score = 0
                    current_subcat_total += score
                            
                subcat_avg = current_subcat_total / len(visible_controls) if visible_controls else 0
                function_total_score += subcat_avg
                
                with st.expander(f"{subcat_key}"):
                    # Professional sub-header for scores
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; background: #F8FAFC; padding: 10px 15px; border-radius: 8px; border: 1px solid #E2E8F0;">
                            <span style="color: #64748B; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Subcategory Maturity</span>
                            <span style="color: #2563EB; font-weight: 800; font-size: 1.1rem;">{subcat_avg:.1f} / 5.0</span>
                        </div>
                        <p style="color: #475569; font-style: italic; font-size: 0.95rem; margin-bottom: 1.5rem;">{subcat_data['description']}</p>
                    """, unsafe_allow_html=True)
                    st.divider()
                    
                    for control in visible_controls:
                        unique_id = f"score_{subcat_key}_{control['id']}"
                        
                        # Auto-Assess Button
                        # Check if key exists for current provider
                        current_provider = st.session_state.get('ai_provider', 'OpenAI')
                        provider_keys = st.session_state.get('provider_keys', {})
                        # Fallback to legacy 'api_key' if 'OpenAI' and not in dict
                        active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
                        
                        if active_key:
                            col_btn, col_empty = st.columns([1, 4])
                            if col_btn.button("✨ Auto-Assess", key=f"btn_{unique_id}", help=f"Analyze with {current_provider}"):
                                with st.spinner(f"Analyzing with {current_provider}..."):
                                    provider_models = st.session_state.get('provider_models', {})
                                    active_model = provider_models.get(current_provider)
                                    
                                    engine = ai_engine.get_engine()
                                    res = engine.assess_control(
                                        control['text'], 
                                        control.get('help', ''), 
                                        active_key,
                                        provider=current_provider,
                                        model_name=active_model
                                    )
                                    st.session_state['ai_results'][unique_id] = res
                                    if 'score' in res and isinstance(res['score'], int):
                                        st.session_state['responses'][unique_id] = res['score']
                                        # Update Widget State (Label)
                                        options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
                                        safe_idx = max(0, min(5, res['score']))
                                        st.session_state[unique_id] = options[safe_idx]
                                    
                                    st.rerun()
                                    
                        # Render Control
                        ai_data = st.session_state['ai_results'].get(unique_id)
                        score = ui.render_control_input(control, unique_id, ai_feedback=ai_data)
                        st.session_state['responses'][unique_id] = score
            
            if not has_visible_controls:
                st.warning(f"No requirements for **{selected_wave_label}** in this category.")
            
            # Rollup for Function (just for internal calculation, not saving this directly)
            nist_function_scores[func] = function_total_score / len(subcats) if subcats else 0

elif page == "History & Dashboard":
    ui.display_header("Assessment Dashboard", "Historical analysis and visualizations")
    
    df = storage.load_history()
    
    if df.empty:
        st.info("No assessments found.")
    else:
        # Selection Logic
        assessment_options = {f"{row['project_name']} ({row['timestamp']})": row['id'] for index, row in df.iterrows()}
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
