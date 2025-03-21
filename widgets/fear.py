# widgets/fear.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Configuration
CACHE_TTL = 7200  # 2 hours cache
INDEX_SYMBOL = "^GSPC"  # S&P 500
VIX_SYMBOL = "^VIX"     # Volatility Index

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_market_data(symbol: str, period: str, interval: str) -> pd.DataFrame:
    """Fetch financial data with robust error handling"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        return hist[~hist.index.duplicated()]  # Remove duplicate timestamps
    except Exception as e:
        st.error(f"Error fetching {symbol} data: {str(e)}")
        return pd.DataFrame()

def calculate_component_momentum(df: pd.DataFrame) -> float:
    """Calculate momentum score (0-100 scale)"""
    if df.empty or len(df) < 125:
        return 50.0
    
    ma_125 = df['Close'].rolling(125).mean().iloc[-1]
    current = df['Close'].iloc[-1]
    
    if pd.isna(ma_125) or ma_125 == 0:
        return 50.0
    
    momentum = ((current - ma_125) / ma_125) * 100
    return np.clip((momentum + 10) * 5, 0, 100)

def calculate_component_strength(df: pd.DataFrame) -> float:
    """Calculate price strength score (0-100 scale)"""
    if df.empty or len(df) < 252:
        return 50.0
    
    high_52w = df['High'].rolling(252).max().iloc[-1]
    low_52w = df['Low'].rolling(252).min().iloc[-1]
    current = df['Close'].iloc[-1]
    
    if high_52w == low_52w or pd.isna(high_52w):
        return 50.0
    
    strength = ((current - low_52w) / (high_52w - low_52w)) * 100
    return np.clip(strength, 0, 100)

def calculate_component_volatility(vix_df: pd.DataFrame) -> float:
    """Calculate volatility score (0-100 scale)"""
    if vix_df.empty or len(vix_df) < 50:
        return 50.0
    
    vix_ma50 = vix_df['Close'].rolling(50).mean().iloc[-1]
    vix_current = vix_df['Close'].iloc[-1]
    
    if pd.isna(vix_ma50) or vix_ma50 == 0:
        return 50.0
    
    volatility = ((vix_current - vix_ma50) / vix_ma50) * 100
    return np.clip(100 - (volatility + 20) * 2.5, 0, 100)  # Correction appliquée ici

@st.cache_data(ttl=3600)
def calculate_fear_greed_index() -> dict:
    """Main calculation function with fallback logic"""
    sp500 = get_market_data(INDEX_SYMBOL, "1y", "1d")
    vix = get_market_data(VIX_SYMBOL, "50d", "1d")
    
    components = {
        "momentum": calculate_component_momentum(sp500),
        "strength": calculate_component_strength(sp500),
        "volatility": calculate_component_volatility(vix)
    }
    
    valid_scores = [v for v in components.values() if not np.isnan(v)]
    composite = np.mean(valid_scores) if valid_scores else 50.0
    
    return {
        **components,
        "composite": composite,
        "timestamp": datetime.now().isoformat(),
        "error": None if not sp500.empty and not vix.empty else "Missing market data"
    }

def create_sentiment_gauge(score: float) -> go.Figure:
    """Create interactive gauge chart with professional styling"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'font': {'size': 28, 'color': "#FFFFFF"},
            'suffix': "%",
            'valueformat': ".1f"
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "#FFFFFF",
                'tickfont': {'color': "#FFFFFF"}
            },
            'bar': {'color': "rgba(255,255,255,0.3)"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#FF4B4B'},
                {'range': [25, 45], 'color': '#FF8C8C'},
                {'range': [45, 55], 'color': '#FFD700'},
                {'range': [55, 75], 'color': '#90EE90'},
                {'range': [75, 100], 'color': '#34C759'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#FFFFFF"},
        annotations=[{
            'text': "Market Sentiment Index",
            'font': {'size': 20},
            'showarrow': False,
            'x': 0.5,
            'y': 0.4
        }]
    )
    return fig

def display_fear_greed_widget():
    """Main widget display function"""
    st.markdown("""
    <style>
    .sentiment-header {
        text-align: center;
        margin-bottom: 30px !important;
    }
    .component-card {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.spinner("Analyzing market conditions..."):
        data = calculate_fear_greed_index()
    
    if data["error"]:
        st.error("Market data unavailable - please try again later")
        return

    score = data["composite"]
    sentiment_config = {
        "Extreme Fear": {"emoji": "😱", "color": "#FF4B4B", "range": (0, 25)},
        "Fear": {"emoji": "😨", "color": "#FF8C8C", "range": (25, 45)},
        "Neutral": {"emoji": "😐", "color": "#FFD700", "range": (45, 55)},
        "Greed": {"emoji": "😎", "color": "#90EE90", "range": (55, 75)},
        "Extreme Greed": {"emoji": "🤑", "color": "#34C759", "range": (75, 100)}
    }

    current_sentiment = next(
        (k for k, v in sentiment_config.items() if v["range"][0] <= score <= v["range"][1]),
        "Neutral"
    )

    # Header
    st.markdown(f"""
    <div class="sentiment-header">
        <h2 style="color:{sentiment_config[current_sentiment]['color']};">
            {sentiment_config[current_sentiment]['emoji']} {current_sentiment}
        </h2>
   
    </div>
    """, unsafe_allow_html=True)

    # Gauge Chart
    st.plotly_chart(create_sentiment_gauge(score), use_container_width=True)

    # Component Breakdown
    st.markdown("### Market Sentiment Components")
    
    components = [
        ("Momentum", data["momentum"], "#FFD700", 
         "S&P 500 vs 125-day moving average"),
        ("Price Strength", data["strength"], "#34C759",
         "Position relative to 52-week range"),
        ("Volatility", data["volatility"], "#FF4B4B",
         "VIX vs 50-day average")
    ]
    
    for name, value, color, desc in components:
        with st.container(border=False):
            cols = st.columns([1, 3])
            with cols[0]:
                st.markdown(f"<div style='font-size:24px; color:{color};'>{value:.1f}</div>", 
                           unsafe_allow_html=True)
            with cols[1]:
                st.subheader(name)
                st.caption(desc)

    # Data Freshness
    updated_time = pd.to_datetime(data["timestamp"]).strftime("%Y-%m-%d %H:%M UTC")
    st.caption(f"Last update: {updated_time}")

# Example usage
if __name__ == "__main__":
    display_fear_greed_widget()