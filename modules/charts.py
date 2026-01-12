import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

def plot_radar_chart(categories, scores):
    """
    Generate a Silicon Precision Radar Chart with glowing effects.
    """
    fig = go.Figure()
    
    # Add the glowing fill
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.2)',
        name='Maturity Level',
        line=dict(color='#2563EB', width=3),
        marker=dict(color='#4F46E5', size=8),
        hovertemplate="<b>%{theta}</b><br>Score: %{r}/5<extra></extra>"
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                gridcolor='#E2E8F0',
                tickfont=dict(size=10, color='#64748B'),
                dtick=1
            ),
            angularaxis=dict(
                gridcolor='#E2E8F0',
                tickfont=dict(size=11, color='#1E293B', family='Plus Jakarta Sans'),
            )
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=60, t=40, b=40),
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_bar_chart(data_dict):
    """
    Generate a Silicon Precision Bar Chart with professional gradients.
    """
    categories = list(data_dict.keys())
    scores = list(data_dict.values())
    
    fig = px.bar(
        x=categories, 
        y=scores,
        color=scores,
        color_continuous_scale=[[0, '#DBEAFE'], [0.5, '#3B82F6'], [1, '#1E3A8A']],
        range_y=[0, 5],
        text_auto='.1f'
    )
    
    fig.update_traces(
        marker_line_width=0,
        marker_pattern_shape="",
        hovertemplate="<b>%{x}</b><br>Maturity: %{y}/5<extra></extra>"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="",
            gridcolor='#F1F5F9',
            tickfont=dict(size=11, color='#475569')
        ),
        yaxis=dict(
            title="Maturity Score",
            gridcolor='#F1F5F9',
            tickfont=dict(size=11, color='#475569'),
            dtick=1
        ),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
        font=dict(family='Plus Jakarta Sans')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
