import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

def plot_radar_chart(categories, scores):
    """
    Generate a Radar Chart for maturity levels.
    """
    df = pd.DataFrame(dict(
        r=scores,
        theta=categories
    ))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Current Maturity',
        line_color='#2874A6'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_bar_chart(data_dict):
    """
    Generate a simple bar chart for scores.
    """
    categories = list(data_dict.keys())
    scores = list(data_dict.values())
    
    fig = px.bar(
        x=categories, 
        y=scores, 
        labels={'x': 'Category', 'y': 'Maturity Score (0-5)'},
        color=scores,
        color_continuous_scale='Blues',
        range_y=[0, 5]
    )
    fig.update_layout(
         margin=dict(l=20, r=20, t=20, b=20),
         height=300
    )
    st.plotly_chart(fig, use_container_width=True)
