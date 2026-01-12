import streamlit as st

def load_custom_css():
    """Inject custom CSS for a professional look."""
    st.markdown("""
        <style>
            /* === SILICON PRECISION DESIGN SYSTEM (Option C) === */
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
            
            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Main App Container */
            html, body, [data-testid="stAppViewContainer"] {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                background: linear-gradient(160deg, #E2E8F0 0%, #F0F4F8 100%) !important;
                color: #0F172A !important;
            }

            /* Block Container Spacing */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 5rem !important;
                max-width: 92% !important;
            }
            
            [data-testid="stHeader"] {
                display: none;
            }
            
            /* === GLASS ELEMENTS === */
            .glass-card {
                background: rgba(255, 255, 255, 0.45) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                border-radius: 20px !important;
                box-shadow: 
                    0 4px 6px -1px rgba(0, 0, 0, 0.05),
                    0 10px 15px -3px rgba(31, 38, 135, 0.08),
                    inset 0 0 20px rgba(255, 255, 255, 0.3) !important;
                padding: 1.8rem;
                margin-bottom: 1.8rem;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .glass-card:hover {
                transform: translateY(-4px);
                background: rgba(255, 255, 255, 0.55) !important;
                box-shadow: 0 20px 25px -5px rgba(31, 38, 135, 0.15) !important;
                border: 1px solid rgba(255, 255, 255, 0.7) !important;
            }

            /* Glass Sidebar */
            [data-testid="stSidebar"] {
                background-color: rgba(255, 255, 255, 0.8) !important;
                backdrop-filter: blur(10px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.5) !important;
            }

            /* Sidebar Nav Active Item Styling */
            [data-testid="stSidebarNav"] ul li div[data-testid="stSidebarNavItem"] {
                border-radius: 10px !important;
                margin: 4px 12px !important;
                padding: 8px 12px !important;
                transition: all 0.2s ease !important;
            }
            
            /* === BUTTONS (Silicon Precision Gradients) === */
            .stButton>button {
                width: 100%;
                border-radius: 12px !important;
                height: 3.4em !important;
                background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
                letter-spacing: -0.01em;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 8px 15px rgba(37, 99, 235, 0.25);
            }
            
            .stButton>button:hover {
                background: linear-gradient(135deg, #1D4ED8 0%, #4338CA 100%) !important;
                box-shadow: 0 12px 24px rgba(37, 99, 235, 0.35) !important;
                transform: translateY(-2px);
            }
            
            /* Secondary/Ghost Buttons */
            div[data-testid="stColumn"] .stButton>button, 
            .stDownloadButton>button {
                background: rgba(255, 255, 255, 0.6) !important;
                backdrop-filter: blur(8px) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                color: #475569 !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03) !important;
            }
            
            /* === SEMANTIC NOTIFICATIONS === */
            .stSuccess, .stInfo, .stWarning, .stError {
                border-radius: 16px !important;
                border: 1px solid rgba(255, 255, 255, 0.5) !important;
                backdrop-filter: blur(12px) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            }
            
            .stSuccess { background-color: rgba(16, 185, 129, 0.15) !important; color: #065F46 !important; border-left: 6px solid #10B981 !important; }
            .stInfo { background-color: rgba(59, 130, 246, 0.15) !important; color: #1E40AF !important; border-left: 6px solid #3B82F6 !important; }
            .stWarning { background-color: rgba(245, 158, 11, 0.15) !important; color: #92400E !important; border-left: 6px solid #F59E0B !important; }
            .stError { background-color: rgba(239, 68, 68, 0.15) !important; color: #991B1B !important; border-left: 6px solid #EF4444 !important; }

            /* === METRICS & DATA DISPLAY === */
            [data-testid="stMetricValue"] {
                color: #0F172A !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 800 !important;
                font-size: 2.4rem !important;
                letter-spacing: -0.05em !important;
            }
            [data-testid="stMetricLabel"] {
                color: #64748B !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                font-size: 0.8rem !important;
                letter-spacing: 0.12em !important;
            }

            /* === PROGRESS BAR (Glowing Gradient) === */
            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #2563EB 0%, #8B5CF6 100%) !important;
                box-shadow: 0 0 20px rgba(37, 99, 235, 0.4) !important;
            }

            /* === TYPOGRAPHY === */
            h1 { font-size: 2.8rem !important; font-weight: 800 !important; letter-spacing: -0.05em !important; color: #0F172A; }
            h2 { font-size: 1.8rem !important; font-weight: 700 !important; letter-spacing: -0.03em !important; color: #1E293B; }
            h3 { font-size: 1.4rem !important; font-weight: 700 !important; color: #334155; }
            
            /* Mono Font for citations/technical data */
            .mono-text {
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 0.85rem !important;
                background: rgba(241, 245, 249, 0.7) !important;
                backdrop-filter: blur(4px) !important;
                padding: 4px 10px !important;
                border-radius: 8px !important;
                border: 1px solid rgba(226, 232, 240, 0.8) !important;
            }

            /* === INPUTS === */
            .stTextInput input, .stSelectbox select, .stTextArea textarea {
                border-radius: 12px !important;
                border: 1px solid rgba(226, 232, 240, 0.8) !important;
                background-color: rgba(255, 255, 255, 0.8) !important;
                padding: 12px 16px !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                backdrop-filter: blur(4px) !important;
            }
            .stTextInput input:focus {
                border-color: #2563EB !important;
                box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15) !important;
            }

            /* Tabs Customization (Linear Look) */
            .stTabs [data-baseweb="tab-list"] { 
                gap: 24px !important;
                border-bottom: 1px solid rgba(226, 232, 240, 0.8) !important;
            }
            .stTabs [data-baseweb="tab"] {
                height: 52px !important;
                font-weight: 700 !important;
                color: #64748B !important;
                border-bottom: 3px solid transparent !important;
            }
            .stTabs [aria-selected="true"] {
                color: #2563EB !important;
                border-bottom: 3px solid #2563EB !important;
            }
        </style>
    """, unsafe_allow_html=True)

def display_header(title, subtitle=""):
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="margin-bottom: 0;">{title}</h1>
            <p style="color: #666; font-size: 1.2rem; margin-top: 0.5rem;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_control_input(control, unique_key, ai_feedback=None):
    """Render a single CSA control input with Silicon Precision Glassmorphism."""
    current_val = st.session_state.get(unique_key, 0)
    is_active = (isinstance(current_val, int) and current_val > 0)
    
    # Try to parse if it's a string from legacy dropdowns
    if not is_active and isinstance(current_val, str) and "(" in current_val:
        try:
            val_num = int(current_val.split('(')[-1].strip(')'))
            if val_num > 0: is_active = True
        except: pass

    with st.container():
        # Glass Card Wrapper
        st.markdown(f'<div class="glass-card" style="border-left: 5px solid {"#2563EB" if is_active else "#E2E8F0"} !important;">', unsafe_allow_html=True)
        
        # Header: ID Badge & Quick Status
        col_id, col_stat = st.columns([5, 1])
        with col_id:
            st.markdown(f"""
                <span style="background: rgba(37, 99, 235, 0.1); 
                             color: #2563EB; 
                             padding: 4px 10px; 
                             border-radius: 6px; 
                             font-weight: 800; 
                             font-size: 0.7rem;
                             text-transform: uppercase;
                             letter-spacing: 0.05em;
                             border: 1px solid rgba(37, 99, 235, 0.2);">
                    {control['id']}
                </span>
            """, unsafe_allow_html=True)
        
        with col_stat:
            if is_active:
                st.markdown('<div style="text-align: right;"><span title="Verified" style="color: #10B981;">●</span></div>', unsafe_allow_html=True)

        # Content: Question & Help
        st.markdown(f"""
            <div style="margin: 1rem 0;">
                <h3 style="margin: 0 0 0.5rem 0; line-height: 1.4;">{control['text']}</h3>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.6; margin: 0;">{control['help']}</p>
            </div>
        """, unsafe_allow_html=True)

        # AI Contextual Feedback (Source Panel)
        if ai_feedback:
             sources_html = "".join([f'<span class="mono-text" style="color: #4F46E5; margin-right: 6px;">{s}</span>' for s in ai_feedback.get('sources', [])])
             st.markdown(f"""
             <div style="background: rgba(248, 250, 252, 0.8); border-radius: 10px; padding: 1rem; border: 1px solid #E2E8F0; margin-bottom: 1.2rem;">
                 <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.5"><path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>
                    <strong style="font-size: 0.8rem; color: #1E293B; text-transform: uppercase; letter-spacing: 0.05em;">AI Intelligence</strong>
                 </div>
                 <div style="font-size: 0.92rem; color: #334155; line-height: 1.5; margin-bottom: 10px;">
                    {ai_feedback.get('justification', 'No analysis details available.')}
                 </div>
                 <div style="border-top: 1px solid #F1F5F9; padding-top: 8px; font-size: 0.75rem;">
                    <span style="color: #94A3B8; font-weight: 600; margin-right: 8px;">CITATIONS:</span> {sources_html if sources_html else '<span style="color: #CBD5E1;">None</span>'}
                 </div>
             </div>
             """, unsafe_allow_html=True)
        
        # Maturity Selector (The Slider)
        options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
        current_idx = max(0, min(5, int(current_val) if isinstance(current_val, (int, float)) else 0))
        
        # Close the Glass Card div before rendering Streamlit widgets (safety first)
        st.markdown("</div>", unsafe_allow_html=True)
        
        selected_label = st.select_slider(
            "Set Maturity Level",
            options=options,
            value=options[current_idx],
            key=unique_key,
            label_visibility="collapsed"
        )
        
        return options.index(selected_label)
