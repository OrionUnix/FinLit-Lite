import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

# Configuration centralisée (importée depuis asset.py)
APP_CONFIG = {
    "colors": {
        "positive": "#34C759",
        "negative": "#FF4B4B",
        "neutral": "#898fa3"
    },
    "chart_height": 400,
    "gauge_height": 200
}

def create_price_chart(df, chart_type="Candlestick", indicators=None, key="price_chart"):
    fig = go.Figure()
    
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                                     name="Price", increasing_line_color=APP_CONFIG["colors"]["positive"],
                                     decreasing_line_color=APP_CONFIG["colors"]["negative"]))
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", line=dict(color=APP_CONFIG["colors"]["positive"]), name="Price"))

    if indicators:
        if "Bollinger Bands" in indicators:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='rgba(150,150,150,0.5)'), name="BB Upper"))
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='rgba(150,150,150,0.5)'), name="BB Lower", fill='tonexty'))
        if "OBV" in indicators:
            fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], line=dict(color='blue'), name="OBV", yaxis="y2"))
        if "Ichimoku Cloud" in indicators:
            fig.add_trace(go.Scatter(x=df.index, y=df['SenkouA'], line=dict(color='green'), name="Senkou A"))
            fig.add_trace(go.Scatter(x=df.index, y=df['SenkouB'], line=dict(color='red'), name="Senkou B", fill='tonexty'))

    fig.update_layout(
        title="Price History (1 Year)", yaxis_title="Price ($)", xaxis_title="Date", template="plotly_white",
        height=APP_CONFIG["chart_height"], margin=dict(t=40, b=20),
        yaxis2=dict(title="OBV", overlaying="y", side="right", showgrid=False) if "OBV" in (indicators or []) else None,
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True, key=key)

def create_gauge(name, value, min_val, max_val, description, key):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value if pd.notna(value) else min_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': name},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': APP_CONFIG["colors"]["positive"] if value >= (max_val + min_val)/2 else APP_CONFIG["colors"]["negative"]},
            'threshold': {'line': {'color': "red", 'width': 2}, 'value': max_val * 0.8 if max_val > 0 else min_val * 0.8}
        }
    ))
    fig.update_layout(height=APP_CONFIG["gauge_height"], margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True, key=key)