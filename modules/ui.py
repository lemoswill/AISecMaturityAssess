import streamlit as st

def load_custom_css():
    """Inject custom CSS for a professional look."""
    st.markdown("""
        <style>
            /* === ENTERPRISE INTELLIGENCE DESIGN SYSTEM === */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Main App Container */
            html, body, [data-testid="stAppViewContainer"] {
                font-family: 'Inter', sans-serif;
                background-color: #F8FAFC;
                color: #0F172A;
            }

            /* Reduce Top Padding (The "Word enter" logic) */
            .block-container {
                padding-top: 0rem !important;
                padding-bottom: 3rem !important;
                max-width: 95% !important;
            }
            
            [data-testid="stHeader"] {
                display: none;
            }
            
            /* === SIDEBAR BRANDING === */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
                border-right: 2px solid #CBD5E1;
            }
            
            [data-testid="stSidebar"] > div:first-child {
                padding-top: 2rem;
            }

            /* === BUTTONS (Unified Styling) === */
            .stButton>button {
                width: 100%;
                border-radius: 8px;
                height: 3em;
                background: #1E3A8A; /* Deep Blue - Primary Action */
                color: #FFFFFF;
                border: none;
                font-weight: 600;
                font-size: 0.95rem;
                letter-spacing: 0.3px;
                transition: all 0.2s ease;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            .stButton>button:hover {
                background: #1E40AF;
                box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
                transform: translateY(-1px);
            }
            
            /* Secondary Buttons (Locker, Cancel) */
            div[data-testid="stColumn"] .stButton>button {
                background: #FFFFFF;
                border: 2px solid #CBD5E1;
                color: #475569;
            }
            
            div[data-testid="stColumn"] .stButton>button:hover {
                background: #F1F5F9;
                border-color: #94A3B8;
                color: #1E293B;
            }

            /* === SEMANTIC COLORS === */
            
            /* Success (Green) */
            .stSuccess, [data-baseweb="notification"][kind="success"] {
                background-color: #D1FAE5 !important;
                border-left: 4px solid #10B981 !important;
                color: #065F46 !important;
            }
            
            /* Warning (Gold) */
            .stWarning, [data-baseweb="notification"][kind="warning"] {
                background-color: #FEF3C7 !important;
                border-left: 4px solid #F59E0B !important;
                color: #92400E !important;
            }
            
            /* Info (Blue) */
            .stInfo, [data-baseweb="notification"][kind="info"] {
                background-color: #DBEAFE !important;
                border-left: 4px solid #3B82F6 !important;
                color: #1E3A8A !important;
            }
            
            /* Error (Red) */
            .stError, [data-baseweb="notification"][kind="error"] {
                background-color: #FEE2E2 !important;
                border-left: 4px solid #EF4444 !important;
                color: #991B1B !important;
            }

            /* === METRICS === */
            [data-testid="stMetricValue"] {
                color: #1E3A8A !important;
                font-family: 'Inter', sans-serif;
                font-weight: 700 !important;
                font-size: 1.5rem !important;
            }
            [data-testid="stMetricLabel"] {
                color: #475569 !important;
                font-weight: 600 !important;
                text-transform: uppercase;
                font-size: 0.75rem !important;
                letter-spacing: 0.05em;
            }
            [data-testid="stMetricDelta"] {
                color: #0066CC !important;
            }

            /* === PROGRESS BAR === */
            .stProgress > div > div > div > div {
                background: linear-gradient(90deg, #0066CC 0%, #3B82F6 100%);
            }

            /* === CONTROL CARDS === */
            .control-card {
                background-color: #FFFFFF;
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                margin-bottom: 1rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
                transition: all 0.2s ease;
            }
            .control-card:hover {
                border-color: #CBD5E1;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            /* === TABS === */
            .stTabs [data-baseweb="tab-list"] {
                gap: 16px;
                border-bottom: 2px solid #E2E8F0;
                padding-bottom: 0;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: transparent;
                border-bottom: 3px solid transparent;
                color: #64748B;
                font-weight: 600;
                font-size: 0.95rem;
                padding: 12px 20px;
                transition: all 0.2s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                color: #475569;
                border-bottom-color: #CBD5E1;
            }
            .stTabs [aria-selected="true"] {
                color: #1E3A8A !important;
                border-bottom-color: #0066CC !important;
            }

            /* === TYPOGRAPHY === */
            h1, h2, h3, h4 {
                color: #0F172A;
                font-weight: 700;
                letter-spacing: -0.02em;
            }
            
            /* === INPUTS === */
            .stTextInput input, .stSelectbox select {
                border-radius: 8px !important;
                border: 2px solid #E2E8F0 !important;
                font-size: 0.95rem !important;
            }
            .stTextInput input:focus, .stSelectbox select:focus {
                border-color: #0066CC !important;
                box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
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
    """Render a single CSA control input with better styling."""
    # Determine if highlighted (score > 0)
    current_val = st.session_state.get(unique_key, 0)
    is_active = False
    if isinstance(current_val, int) and current_val > 0:
        is_active = True
    elif isinstance(current_val, str) and "(" in current_val:
        # Check if number in "(N)" is > 0
        try:
            val_num = int(current_val.split('(')[-1].strip(')'))
            if val_num > 0: is_active = True
        except:
            pass

    # Use a styled container with native Streamlit components
    with st.container():
        # Custom CSS for this specific card
        card_border_color = "#0066CC" if is_active else "#E2E8F0"
        
        st.markdown(f"""
            <style>
                .control-card-{control['id'].replace('.', '-')} {{
                    background-color: #FFFFFF;
                    padding: 1.5rem;
                    border-radius: 10px;
                    border: 1px solid {card_border_color};
                    margin-bottom: 1rem;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
                }}
            </style>
            <div class="control-card-{control['id'].replace('.', '-')}">
        """, unsafe_allow_html=True)
        
        # Header row with ID badge and active indicator
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
                <span style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                             color: #1E3A8A; 
                             padding: 4px 12px; 
                             border-radius: 6px; 
                             font-weight: 700; 
                             font-size: 0.75rem;
                             border: 1px solid #BFDBFE;
                             letter-spacing: 0.5px;
                             display: inline-block;">
                    {control['id']}
                </span>
            """, unsafe_allow_html=True)
        
        with col2:
            if is_active:
                st.markdown("""
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="10" cy="10" r="8" fill="#0066CC" fill-opacity="0.1" stroke="#0066CC" stroke-width="2"/>
                        <path d="M6 10L9 13L14 8" stroke="#0066CC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                """, unsafe_allow_html=True)
        
        # Control text (question)
        st.markdown(f"""
            <div style="color: #0F172A; font-weight: 600; font-size: 1.05rem; line-height: 1.5; margin: 12px 0 8px 0;">
                {control['text']}
            </div>
        """, unsafe_allow_html=True)
        
        # Help text (description)
        st.markdown(f"""
            <div style="color: #64748B; font-size: 0.875rem; line-height: 1.6;">
                {control['help']}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # AI Feedback Display
        if ai_feedback:
             st.markdown(f"""
             <div style="background-color: #f0f7ff; padding: 10px; border-radius: 5px; border: 1px solid #cce5ff; margin-bottom: 10px; font-size: 0.9em;">
                 <strong>🤖 AI Analysis:</strong> {ai_feedback.get('justification', 'No details.')}<br>
                 <span style="color: #666; font-size: 0.85em;">Sources: {', '.join(ai_feedback.get('sources', []))}</span>
             </div>
             """, unsafe_allow_html=True)
        
        # Mapping for Slider
        options = ["Not Implemented (0)", "Initial (1)", "Defined (2)", "Managed (3)", "Measured (4)", "Optimized (5)"]
        
        # Convert numeric score to label index
        current_val = st.session_state.get(unique_key, 0)
        # Ensure it's an int and within bounds
        if not isinstance(current_val, int): current_val = 0
        current_val = max(0, min(5, current_val))
        
        selected_label = st.select_slider(
            "Maturity Level",
            options=options,
            value=options[current_val],
            key=unique_key,
            label_visibility="collapsed"
        )
        
        # Return numeric value (extract first char or use index)
        return options.index(selected_label)
