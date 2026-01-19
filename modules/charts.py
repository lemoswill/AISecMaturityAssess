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
    
    return fig

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
    
    return fig

def plot_gauge_chart(score, max_score=5.0):
    """
    Generate an Executive Gauge Chart (0-100 scale).
    """
    # Convert 0-5 scale to 0-100
    percentage = (score / max_score) * 100
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Security Maturity Score", 'font': {'size': 20, 'color': '#1E293B', 'family': 'Inter'}},
        number = {'suffix': "%", 'font': {'size': 40, 'color': '#0F172A', 'family': 'Inter', 'weight': 700}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
            'bar': {'color': "#2563EB", 'thickness': 0.75}, # Removed alpha from color hex
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 25], 'color': '#FEE2E2'},
                {'range': [25, 50], 'color': '#FEF3C7'},
                {'range': [50, 75], 'color': '#D1FAE5'},
                {'range': [75, 100], 'color': '#DBEAFE'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#1E293B", 'family': "Inter"},
        margin=dict(l=30, r=30, t=50, b=10),
        height=300
    )
    
    return fig

def plot_benchmark_chart(your_scores, industry_scores=None):
    """
    Generate a Comparison Bar Chart (You vs Industry).
    """
    categories = list(your_scores.keys())
    y_values = list(your_scores.values())
    
    if not industry_scores:
        # Generate synthetic industry data if not provided (Benchmark)
        # Assume industry avg is around 3.2 (Managed)
        industry_scores = {k: 3.2 for k in categories}
    
    i_values = list(industry_scores.values())

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=y_values,
        name='Your Score',
        marker_color='#2563EB',
        hovertemplate="<b>%{x}</b><br>You: %{y}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=i_values,
        name='Industry Avg',
        marker_color='#94A3B8',
        hovertemplate="<b>%{x}</b><br>Industry: %{y}<extra></extra>"
    ))

    fig.update_layout(
        barmode='group',
        title="Benchmark Analysis",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            range=[0, 5], 
            gridcolor='#F1F5F9',
            dtick=1
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0)'
        ),
        font=dict(family='Inter'),
        margin=dict(l=20, r=20, t=60, b=20),
        height=350
    )
    
    return fig
