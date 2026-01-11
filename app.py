__import__('pysqlite3')
import sys
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
<div style="text-align: center; padding: 1.5rem 0 1.5rem 0; border-bottom: 2px solid #E2E8F0; margin-bottom: 1.5rem;">
    <svg width="56" height="56" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 12px;">
        <path d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z" 
              stroke="#0066CC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="#0066CC" fill-opacity="0.1"/>
        <path d="M9 12L11 14L15 10" stroke="#0066CC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <h2 style="color: #0F172A; margin: 0; font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em;">AI Security</h2>
    <p style="color: #64748B; margin: 6px 0 0 0; font-size: 0.8rem; font-weight: 500;">Maturity Assessment Platform</p>
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
    st.markdown("### 🤖 AI Provider")
    
    # Initialize session state for provider settings if not exists
    if 'provider_keys' not in st.session_state:
        st.session_state['provider_keys'] = {}
    if 'provider_models' not in st.session_state:
        st.session_state['provider_models'] = {}

    provider_options = ["OpenAI", "Gemini", "Perplexity", "Ollama (Local)"]
    provider_selected = st.selectbox("Select Intelligence Provider", provider_options, index=0)
    provider_clean = provider_selected.split(" (")[0]
    st.session_state['ai_provider'] = provider_clean
    
    current_key = st.session_state['provider_keys'].get(provider_clean, "")
    current_model = st.session_state['provider_models'].get(provider_clean, "")

    if provider_clean == "Ollama":
        col1, col2 = st.columns([2, 3])
        with col1:
            ollama_host = st.text_input("Ollama Host URL", value=current_key if current_key else "http://localhost:11434", placeholder="e.g. http://localhost:11434")
            st.session_state['provider_keys'][provider_clean] = ollama_host
            
            # Fetch local models automatically
            engine = ai_engine.get_engine()
            local_models = engine.list_local_models(ollama_host)
            
        with col2:
            if local_models:
                # Use selectbox if models are found
                index = 0
                if current_model in local_models:
                    index = local_models.index(current_model)
                elif "deepseek-r1" in local_models:
                    index = local_models.index("deepseek-r1")
                
                ollama_model = st.selectbox("Select Local Model", local_models, index=index)
                st.session_state['provider_models'][provider_clean] = ollama_model
                
                if st.button("🔄 Refresh Model List"):
                    st.rerun()
            else:
                # Fallback to text input if no connection or no models
                st.warning("Could not list local models. Is Ollama running?")
                ollama_model = st.text_input("Model Name (Manual)", value=current_model if current_model else "deepseek-r1")
                st.session_state['provider_models'][provider_clean] = ollama_model
                
                if st.button("🔌 Try Reconnect"):
                    st.rerun()
        
        st.info("💡 Ensure Ollama is running (`ollama serve`) and you have the model pulled (e.g., `ollama pull deepseek-r1`).")
    else:
        col1, col2 = st.columns(2)
        with col1:
            help_text = "Required for Auto-Assessment"
            if provider_clean == "Gemini": help_text = "Get from Google AI Studio"
            elif provider_clean == "Perplexity": help_text = "Get from perplexity.ai/api"
            
            new_key = st.text_input(f"{provider_clean} API Key", value=current_key, type="password", help=help_text)
            st.session_state['provider_keys'][provider_clean] = new_key
            # Legacy support for some modules
            st.session_state['api_key'] = new_key
        with col2:
            default_model = "gpt-3.5-turbo" if provider_clean == "OpenAI" else "gemini-pro" if provider_clean == "Gemini" else "sonar"
            new_model = st.text_input("Model Name (Optional)", value=current_model if current_model else default_model)
            st.session_state['provider_models'][provider_clean] = new_model

    if not st.session_state['provider_keys'].get(provider_clean):
        st.warning(f"Please provide configuration for {provider_clean}.")
        
    st.divider()
    
    # 2. File Upload
    st.markdown("### 📂 Document Ingestion")
    st.info("Upload Policies, Architecture Diagrams (PDF), Playbooks, or Interview Transcripts.")
    
    uploaded_files = st.file_uploader("Upload Evidence", type=['pdf', 'txt', 'md'], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button(f"Process {len(uploaded_files)} Files"):
            with st.spinner("Encrypting and Indexing documents..."):
                engine = ai_engine.get_engine()
                # Clear old DB to avoid duplicates or manage incrementally?
                # For this demo, let's keep it incremental or allow reset.
                
                for up_file in uploaded_files:
                    saved_path = evidence.save_uploaded_file(up_file)
                    if saved_path:
                        success, fast_msg = engine.ingest_file(up_file.name)
                        if success:
                            st.success(f"Indexed: {up_file.name}")
                        else:
                            st.error(f"Failed {up_file.name}: {fast_msg}")
                            
            st.success("Ingestion Complete! You can now use Auto-Assess in the Assessment tab.")
            
    # 3. View Index
    st.divider()
    st.markdown("### 📚 Indexed Knowledge Base")
    files = evidence.list_evidence_files()
    if files:
        for f in files:
            st.text(f"📄 {f}")
        
        if st.button("🗑️ Reset Knowledge Base", type="primary"):
             engine = ai_engine.get_engine()
             if engine.reset_db():
                 st.success("Knowledge Base Wiped.")
                 # Also remove files
                 import shutil
                 if os.path.exists(evidence.EVIDENCE_DIR):
                     shutil.rmtree(evidence.EVIDENCE_DIR)
                     os.makedirs(evidence.EVIDENCE_DIR)
                 st.experimental_rerun()
    else:
        st.info("No documents indexed yet.")

if page == "Assessment":
    ui.display_header("AI Security Maturity Assessment", "NIST AI RMF mapped to CSA AICM Controls")
    
    # --- Enterprise Intelligence Hero Section ---
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); 
                padding: 2rem 2.5rem; 
                border-radius: 12px; 
                margin-bottom: 2rem;
                border: 2px solid #E2E8F0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border-left: 6px solid #0066CC;">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="background: linear-gradient(135deg, #0066CC 0%, #3B82F6 100%); 
                        padding: 15px; 
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0, 102, 204, 0.2);">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z" 
                          stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="white" fill-opacity="0.2"/>
                    <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div style="flex: 1;">
                <h2 style="color: #0F172A; margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em;">
                    Security Intelligence Platform
                </h2>
                <p style="color: #475569; margin: 6px 0 0 0; font-size: 0.95rem; font-weight: 500; line-height: 1.5;">
                    Automated compliance assessment across <strong style="color: #1E3A8A;">NIST AI RMF</strong> and <strong style="color: #1E3A8A;">CSA AICM</strong> frameworks
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
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📂 Go to Evidence Locker", type="primary", use_container_width=True):
                st.session_state['navigate_to'] = 'Evidence Locker 🧠'
                st.rerun()
    else:
        st.success(f"✅ **Evidence Ready** - {len(files)} document(s) indexed")
        
        # Domain Selector
        st.markdown("**Select domain to analyze:**")
        available_domains = list(data.NIST_FUNCTIONS.keys())
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_domain = st.selectbox(
                "Choose NIST Function",
                available_domains,
                format_func=lambda x: f"{x} - {data.NIST_FUNCTIONS[x]}",
                label_visibility="collapsed"
            )
        
        with col2:
            # Check if API key exists
            current_provider = st.session_state.get('ai_provider', 'OpenAI')
            provider_keys = st.session_state.get('provider_keys', {})
            active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
            
            if active_key:
                if st.button(f"🚀 Analyze {selected_domain}", type="primary", use_container_width=True):
                    # Trigger bulk assessment for selected domain
                    st.session_state['trigger_bulk_assess'] = selected_domain
                    st.rerun()
            else:
                st.button("🔑 Configure AI Key", type="secondary", use_container_width=True, disabled=True)
                st.caption("⚠️ Set API key in Evidence Locker")
    
    
    st.markdown("---")
    
    # --- Wave Filter (MUST be before progress calculation) ---
    st.sidebar.markdown("### 🌊 Maturity Phase")
    wave_options = ["All Waves"] + list(data.MATURITY_WAVES.values())
    selected_wave_label = st.sidebar.selectbox("Filter by Phase:", wave_options, index=1) # Default to Wave 1
    
    # Store in session state for progress calculation
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
                        
                        final_responses.append({
                            "category": func,
                            "question_id": control['id'],
                            "score": score,
                            "notes": f"Mapped to {subcat_key}"
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
            # Check for API Key
            current_provider = st.session_state.get('ai_provider', 'OpenAI')
            provider_keys = st.session_state.get('provider_keys', {})
            active_key = provider_keys.get(current_provider, st.session_state.get('api_key') if current_provider == 'OpenAI' else None)
            
            if active_key:
                 if st.button(f"✨ Auto-Assess All ({func})", key=f"bulk_{func}", type="secondary", help=f"Deep analysis of all '{func}' requirements using {current_provider}"):
                    
                    # Gather controls first to know total
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
                        
                        for idx, ctrl in enumerate(target_controls):
                            status_text.text(f"Analyzing {idx+1}/{len(target_controls)}: {ctrl['id']}...")
                            
                        # Retry loop with correct key access
                        count = 0
                        for sk, sd in subcats_bulk.items():
                            c_list = sd.get('csa_controls', [])
                            # Filter
                            valid_c = [c for c in c_list if (selected_wave_id is None) or (c.get('wave', 2) == selected_wave_id)]
                            
                            for c in valid_c:
                                count += 1
                                status_text.text(f"Analyzing {count}/{len(target_controls)}: {c['id']} - {c['text'][:50]}...")
                                progress_bar.progress(count / len(target_controls))
                                
                                unique_id = f"score_{sk}_{c['id']}"
                                
                                # Call AI
                                try:
                                    res = engine.assess_control(
                                        c['text'], 
                                        c.get('help', ''), 
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
                                except Exception as e:
                                    print(f"Error assessing {c['id']}: {e}")
                                    
                        status_text.text("✅ Analysis Complete!")
                        progress_bar.empty()
                        st.rerun()
            
            st.divider()
            
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
                
                # Calculate current subcat score
                current_subcat_total = 0
                for c in visible_controls:
                    # Use unique key including subcat
                    unique_id = f"score_{subcat_key}_{c['id']}"
                    val = st.session_state.get(unique_id, 0)
                    
                    score = 0
                    if isinstance(val, int):
                        score = val
                    elif isinstance(val, str):
                        # Extract number from "Label (N)"
                        try:
                            score = int(val.split('(')[-1].strip(')'))
                        except:
                            score = 0
                            
                subcat_avg = current_subcat_total / len(visible_controls) if visible_controls else 0
                
                # Using a static label (no dynamic score in header) to prevent auto-closing in all Streamlit versions
                with st.expander(f"{subcat_key}"):
                    # Professional sub-header for scores
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <span style="color: #64748B; font-size: 0.9rem; font-weight: 500;">Current Maturity:</span>
                            <span style="color: #1E3A8A; font-weight: 700; font-size: 1.1rem;">{subcat_avg:.1f} / 5.0</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"_{subcat_data['description']}_")
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
                
                function_total_score += subcat_avg
            
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
            
            # Overview Metrics
            sel_row = df[df['id'] == selected_id].iloc[0]
            
            with st.container():
                col1, col2, col3 = st.columns(3)
                col1.metric("Project Name", sel_row['project_name'])
                col2.metric("Total Score", f"{sel_row['total_score']:.2f} / 5.0")
                col3.metric("Maturity Level", sel_row['maturity_level'])
                
            st.divider()
            
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
