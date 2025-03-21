import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from widgets.technical_charts import create_price_chart, create_gauge

# Configuration de la page
st.set_page_config(page_title="Asset Details", layout="wide")

# Couleurs par défaut
positive_color = "#34C759"  # Vert
negative_color = "#FF4B4B"  # Rouge

@st.cache_data(ttl=3600, show_spinner="Loading asset data...")
def get_asset_data(symbol):
    """Retrieve asset data via yfinance."""
    try:
        asset = yf.Ticker(symbol)
        return {
            "info": asset.info,
            "history": asset.history(period="1y", interval="1d", auto_adjust=False),
            "financials": asset.financials,
            "cashflow": asset.cashflow,
            "dividends": asset.dividends,
            "major_holders": asset.major_holders,
            "institutional_holders": asset.institutional_holders,
            "quarterly_earnings": asset.quarterly_earnings
        }
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
        st.stop()

def calculate_technical(df):
    """Calculate technical indicators manually without pandas_ta."""
    df = df.copy()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Stochastic Oscillator (%K)
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['STOCH_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
    
    # CCI
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    sma_tp = typical_price.rolling(window=20).mean()
    mean_dev = typical_price.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    df['CCI'] = (typical_price - sma_tp) / (0.015 * mean_dev)
    
    # Williams %R
    high_14 = df['High'].rolling(window=14).max()
    low_14 = df['Low'].rolling(window=14).min()
    df['WILLR'] = -100 * (high_14 - df['Close']) / (high_14 - low_14)
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    
    # Chaikin Oscillator (simplifié)
    ad = ((2 * df['Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['Volume']).cumsum()
    df['CHAIKIN'] = ad.ewm(span=3, adjust=False).mean() - ad.ewm(span=10, adjust=False).mean()
    
    # Ultimate Oscillator
    bp = df['Close'] - df['Low'].shift()
    tr = pd.concat([df['High'] - df['Low'], np.abs(df['High'] - df['Close'].shift()), np.abs(df['Low'] - df['Close'].shift())], axis=1).max(axis=1)
    avg7 = (bp.rolling(window=7).sum() / tr.rolling(window=7).sum())
    avg14 = (bp.rolling(window=14).sum() / tr.rolling(window=14).sum())
    avg28 = (bp.rolling(window=28).sum() / tr.rolling(window=28).sum())
    df['UO'] = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7
    
    # Bollinger Bands (bonus)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['MA20'] + (std * 2)
    df['BB_Lower'] = df['MA20'] - (std * 2)
    
    # OBV (bonus)
    df['OBV'] = np.where(df['Close'] > df['Close'].shift(1), df['Volume'], 
                        np.where(df['Close'] < df['Close'].shift(1), -df['Volume'], 0)).cumsum()
    
    # Ichimoku Cloud (bonus)
    high_9, low_9 = df['High'].rolling(9).max(), df['Low'].rolling(9).min()
    df['Tenkan'] = (high_9 + low_9) / 2
    high_26, low_26 = df['High'].rolling(26).max(), df['Low'].rolling(26).min()
    df['Kijun'] = (high_26 + low_26) / 2
    df['SenkouA'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)
    df['SenkouB'] = ((df['High'].rolling(52).max() + df['Low'].rolling(52).min()) / 2).shift(26)
    
    return df

# Sidebar
with st.sidebar:
    st.markdown("""
    ### Welcome to FinLite (Lite Version)  
    This is a free, open-source demo built in Python, showcasing basic portfolio analysis with real-time data (~5-min delay). Explore a sample portfolio, track asset values, and visualize gains/losses. Designed for simplicity and hosted on Streamlit Community Cloud, this is just a taste of FinLite’s potential!
    """)
    symbol = st.query_params.get("symbol", "NVDA")
    st.markdown(f"- 🏠 [Home](/)\n- 📊 [Asset](/asset?symbol={symbol})", unsafe_allow_html=True)
    with st.expander("📈 Paramètres des indicateurs", expanded=False):
        bollinger_enabled = st.checkbox("Bollinger Bands", True)
        ichimoku_enabled = st.checkbox("Ichimoku Cloud", False)
        obv_enabled = st.checkbox("OBV", False)
        selected_indicators = [i for i, enabled in [("Bollinger Bands", bollinger_enabled), 
                                                   ("Ichimoku Cloud", ichimoku_enabled), 
                                                   ("OBV", obv_enabled)] if enabled]

# Récupération des données
asset_data = get_asset_data(symbol)
info = asset_data["info"]
history = calculate_technical(asset_data["history"])

# En-tête principal
st.subheader(f"{info.get('longName', symbol)} ({symbol})")

# Overview
st.markdown("#### Overview")
try:
    overview = info.get("longBusinessSummary", "No description available.")
    website = info.get("website", None)
    st.write(overview[:300] + "..." if len(overview) > 300 else overview)
    if website:
        st.markdown(f"[Visit website]({website})")
except Exception as e:
    st.error(f"Error displaying overview: {str(e)}")

# Layout en deux colonnes
col1, col2 = st.columns([1, 3])

# Colonne gauche - Métriques principales
with col1:
    try:
        price = info.get("regularMarketPrice", info.get("currentPrice", 0))
        prev_close = info.get("regularMarketPreviousClose", history["Close"].iloc[-2] if len(history) > 1 else 0)
        change = price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0
        volume = info.get("regularMarketVolume", 0)
        ask = info.get("ask", "N/A")
        bid = info.get("bid", "N/A")

        background_color = positive_color if change_pct >= 0 else negative_color
        st.markdown(
            f"""
            <div style='border-radius: 10px; border: 1px solid #ccc; padding: 0;'>
                <div style='background-color: {background_color}; color: white; padding: 0.5rem; text-align: center; font-weight: 600; font-size: 1.1rem; border-radius: 10px 10px 0 0;'>
                    {symbol}
                </div>
                <div style='padding: 0.5rem; display: flex; flex-direction: column; gap: 0.2rem;'>
                    <div style='font-size: 0.9rem; font-weight: 500;'>{info.get('longName', symbol)}</div>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <div style='color: {positive_color if change_pct >= 0 else negative_color}; font-size: 0.9rem;'>
                                {'▲' if change_pct >= 0 else '▼'} {abs(change_pct):.2f}%
                            </div>
                            <div style='color: #898fa3; font-size: 0.8rem;'>{change:+.2f}$</div>
                            <div style='color: #898fa3; font-size: 0.8rem;'>({volume:,} vol)</div>
                        </div>
                        <div style='font-size: 1rem; font-weight: bold;'>{price:,.2f}$</div>
                    </div>
                    <div style='color: #898fa3; font-size: 0.8rem; margin-top: 0.2rem;'>
                        Bid: {bid} | Ask: {ask}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Key Metrics")
        st.markdown(
            f"""
            <div style='padding: 0.5rem; border: 1px solid #ccc; border-radius: 5px;'>
                <div>Previous Close: {info.get('regularMarketPreviousClose', 'N/A')}$</div>
                <div>Open: {info.get('regularMarketOpen', 'N/A')}$</div>
                <div>Bid: {bid}$</div>
                <div>Earnings Date: {info.get('earningsDate', 'N/A')}</div>
                <div>Dividend & Yield: {info.get('dividendRate', 'N/A')} ({info.get('dividendYield', 0)*100:.2f}%)</div>
                <div>Ex-Dividend Date: {info.get('exDividendDate', 'N/A')}</div>
                <div>1y Target Est: {info.get('targetMeanPrice', 'N/A')}$</div>
                <div>Market Cap: {info.get('marketCap', 0)/1e9:.2f}B$</div>
                <div>Sector: {info.get('sector', 'N/A')}</div>
                <div>Beta: {info.get('beta', 'N/A')}</div>
                <div>PE Ratio: {info.get('trailingPE', 'N/A')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")

# Colonne droite - Graphique principal
with col2:
    try:
        chart_type = st.radio("Chart Type", ["Candlestick", "Line"], horizontal=True)
        create_price_chart(history, chart_type, selected_indicators, key="main_chart")
    except Exception as e:
        st.error(f"Error displaying chart: {str(e)}")

# Analyse Technique Avancée (RSI et MACD)
st.subheader("Advanced Technical Analysis")
try:
    col1, col2 = st.columns(2)
    with col1:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=history.index, y=history['RSI'], line=dict(color=positive_color), name="RSI"))
        fig_rsi.update_layout(title="RSI (14 days)", yaxis_title="RSI", height=300, showlegend=False, template="plotly_white")
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        st.plotly_chart(fig_rsi, use_container_width=True, key="rsi_chart")
    with col2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=history.index, y=history['MACD'], line=dict(color=positive_color), name="MACD"))
        fig_macd.add_trace(go.Scatter(x=history.index, y=history['MACD_Signal'], line=dict(color=negative_color), name="Signal"))
        fig_macd.update_layout(title="MACD (12/26/9)", yaxis_title="MACD", height=300, template="plotly_white")
        st.plotly_chart(fig_macd, use_container_width=True, key="macd_chart")
except Exception as e:
    st.error(f"Error in technical analysis: {str(e)}")

# Oscillateurs Techniques (Jauges)
st.subheader("Technical Oscillators")
try:
    latest = history.iloc[-1]
    cols = st.columns(4)
    oscillators = [
        ("RSI", latest['RSI'], 0, 100, "Relative Strength Index: Measures speed and change of price movements (0-100). Identifies overbought (>70) or oversold (<30) conditions."),
        ("STOCH_K", latest['STOCH_K'], 0, 100, "Stochastic Oscillator: Compares closing price to its range over 14 days (0-100). Highlights overbought (>80) or oversold (<20) levels."),
        ("CCI", latest['CCI'], -200, 200, "Commodity Channel Index: Measures price deviation from average (-200 to 200). Extreme values indicate potential reversals."),
        ("WILLR", latest['WILLR'], -100, 0, "Williams %R: Momentum oscillator (0 to -100). Identifies overbought (>-20) or oversold (<-80) levels."),
        ("MACD", latest['MACD'] - latest['MACD_Signal'], -10, 10, "MACD Difference: Tracks momentum by comparing two moving averages."),
        ("ATR", latest['ATR'], 0, max(20, latest['ATR'] * 1.5), "Average True Range: Measures volatility based on price range."),
        ("CHAIKIN", latest['CHAIKIN'], -1e9, 1e9, "Chaikin Oscillator: Combines price and volume to assess momentum."),
        ("UO", latest['UO'], 0, 100, "Ultimate Oscillator: Uses multiple timeframes (7/14/28) to measure momentum (0-100).")
    ]
    for i, (name, value, min_val, max_val, desc) in enumerate(oscillators):
        with cols[i % 4]:
            create_gauge(name, value, min_val, max_val, desc, key=f"gauge_{name.lower()}")
            st.write(desc)
except Exception as e:
    st.error(f"Error in oscillators: {str(e)}")

# Analyse Fondamentale
st.subheader("Fundamental Analysis")
try:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Valuation", "Finances", "Dividends", "Competitors", "Performance Overview"])
    with tab1:
        valuation_data = {
            "Ratio": ["P/E", "P/S", "EV/EBITDA", "P/B", "Dividend Yield", "Beta (5Y Monthly)", "EPS (TTM)"],
            "Value": [
                info.get('trailingPE', 'N/A'),
                info.get('priceToSalesTrailing12Months', 'N/A'),
                info.get('enterpriseToEbitda', 'N/A'),
                info.get('priceToBook', 'N/A'),
                f"{info.get('dividendYield', 0)*100:.2f}%",
                info.get('beta', 'N/A'),
                info.get('trailingEps', 'N/A')
            ]
        }
        st.dataframe(pd.DataFrame(valuation_data), hide_index=True)
    with tab2:
        if asset_data['financials'] is not None and not asset_data['financials'].empty:
            rev = asset_data['financials'].loc['Total Revenue'].iloc[0] if 'Total Revenue' in asset_data['financials'].index else 0
            ni = asset_data['financials'].loc['Net Income'].iloc[0] if 'Net Income' in asset_data['financials'].index else 0
            ebitda = asset_data['financials'].loc['Ebit'].iloc[0] if 'Ebit' in asset_data['financials'].index else "N/A"
            gross_profit = asset_data['financials'].loc['Gross Profit'].iloc[0] if 'Gross Profit' in asset_data['financials'].index else "N/A"
            margin = (ni / rev * 100) if rev != 0 else 0
            st.metric("Revenue TTM", f"{rev/1e6:.2f}M$")
            st.metric("Net Margin", f"{margin:.1f}%")
            st.metric("EBITDA", f"{ebitda/1e6:.2f}M$" if isinstance(ebitda, (int, float)) else ebitda)
            st.metric("Gross Profit", f"{gross_profit/1e6:.2f}M$" if isinstance(gross_profit, (int, float)) else gross_profit)
        else:
            st.warning("Financial data not available")
    with tab3:
        st.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%", f"Payout Ratio: {info.get('payoutRatio', 'N/A')}")
        if asset_data['dividends'] is not None and not asset_data['dividends'].empty:
            st.write("### Dividend History (Last 5 Years)")
            five_years_ago = datetime.now().year - 5
            div_history = asset_data['dividends'][asset_data['dividends'].index.year >= five_years_ago]
            if not div_history.empty:
                st.dataframe(div_history.rename("Dividend ($)").to_frame(), hide_index=True)
            else:
                st.write("No dividends paid in the last 5 years.")
        else:
            st.write("No dividend history available.")
    with tab4:
        st.write("### Major Competitors")
        st.write("This is a Lite/Demo version. Competitor data is not available in this release.")
        sector = info.get("sector", "Unknown")
        if sector == "Technology":
            st.write("- Microsoft (MSFT)\n- Google (GOOGL)\n- Amazon (AMZN)")
        elif sector == "Consumer Cyclical":
            st.write("- Tesla (TSLA)\n- Amazon (AMZN)\n- Walmart (WMT)")
        else:
            st.write("Competitor data not readily available in this Lite version.")
    with tab5:
        st.write("### Performance Overview (as of Mar 20, 2025)")
        st.write("Total cumulative returns include dividends or other distributions. Benchmark: S&P 500 (^GSPC).")
        performance_data = {
            "Period": ["YTD", "1 Year", "3 Years", "5 Years"],
            "Symbol": ["N/A", "N/A", "N/A", "N/A"],
            "S&P 500 (^GSPC)": ["3.72%", "8.39%", "26.88%", "145.69%"]
        }
        st.dataframe(pd.DataFrame(performance_data), hide_index=True)

        st.write("### Discounted Cash Flow (DCF) Analysis")
        if asset_data['cashflow'] is not None and 'Free Cash Flow' in asset_data['cashflow'].index:
            fcf = asset_data['cashflow'].loc['Free Cash Flow'].iloc[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                growth = st.slider("FCF Growth Rate (%)", 0.0, 20.0, 8.0, 0.5)
            with col2:
                discount = st.slider("Discount Rate (%)", 5.0, 15.0, 10.0, 0.5)
            with col3:
                terminal = st.slider("Terminal Growth Rate (%)", 0.0, 5.0, 2.5, 0.1)
            if discount > terminal:
                years = 5
                cashflows = [fcf * (1 + growth/100)**i for i in range(1, years+1)]
                terminal_value = cashflows[-1] * (1 + terminal/100) / ((discount - terminal)/100)
                dcf_value = sum(cf / (1 + discount/100)**i for i, cf in enumerate(cashflows, 1)) + terminal_value / (1 + discount/100)**years
                current_mc = info.get('marketCap', 0)
                delta = dcf_value - current_mc
                st.metric("Estimated DCF Value", f"{dcf_value/1e9:.2f}B$", delta=f"{delta/1e9:.2f}B$ vs Market Cap", delta_color="normal" if delta > 0 else "inverse")
            else:
                st.warning("Discount rate must be greater than terminal growth rate")
        else:
            st.warning("Cash flow data not available")
except Exception as e:
    st.error(f"Error in fundamental analysis: {str(e)}")

# Revenue and Earnings
st.subheader("Revenue and Earnings")
try:
    if asset_data['quarterly_earnings'] is not None and not asset_data['quarterly_earnings'].empty:
        quarterly_earnings = asset_data['quarterly_earnings'].tail(4)
        revenue_data = {
            "Quarter": quarterly_earnings.index.strftime("Q%m %Y").tolist(),
            "Revenue (B$)": (quarterly_earnings['Revenue'] / 1e9).tolist(),
            "Earnings (EPS)": quarterly_earnings['Earnings'].tolist()
        }
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=revenue_data["Quarter"], y=revenue_data["Revenue (B$)"], name="Revenue (B$)", marker_color=positive_color))
        fig_bar.add_trace(go.Bar(x=revenue_data["Quarter"], y=revenue_data["Earnings (EPS)"], name="Earnings (EPS)", marker_color=negative_color))
        fig_bar.update_layout(barmode='group', title="Revenue and Earnings by Quarter (Last 4 Quarters)", height=400)
        st.plotly_chart(fig_bar, use_container_width=True, key="revenue_earnings_chart")
    else:
        st.write("Données trimestrielles non disponibles via yfinance.")
except Exception as e:
    st.error(f"Error in revenue and earnings: {str(e)}")

# Shareholders and Insiders
st.subheader("Shareholders and Insiders")
try:
    st.write("### Major Shareholders")
    if asset_data['major_holders'] is not None and not asset_data['major_holders'].empty:
        major_holders = asset_data['major_holders']
        if major_holders.shape[0] > 0:
            shareholders = {
                "Holder": ["Insiders" if i == 0 else "Institutions" if i == 1 else f"Holder {i+1}" for i in range(major_holders.shape[0])],
                "% Out": [major_holders.iloc[i, 1] if major_holders.shape[1] > 1 else "N/A" for i in range(major_holders.shape[0])],
                "Shares": [major_holders.iloc[i, 0] for i in range(major_holders.shape[0])]
            }
            df_shareholders = pd.DataFrame(shareholders)
            df_shareholders['% Out'] = df_shareholders['% Out'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) and isinstance(x, (int, float)) else "N/A")
            df_shareholders['Shares'] = df_shareholders['Shares'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and isinstance(x, (int, float)) else "N/A")
            st.dataframe(df_shareholders, hide_index=True)
        else:
            st.write("Données insuffisantes via yfinance pour ce symbole.")
    else:
        st.write("Non disponible via yfinance pour ce symbole.")

    st.write("### Institutional Holders")
    if asset_data['institutional_holders'] is not None and not asset_data['institutional_holders'].empty:
        inst_holders = asset_data['institutional_holders'].copy()
        inst_holders['Value (B$)'] = inst_holders['Value'] / 1e9
        inst_holders['Shares'] = inst_holders['Shares'].astype(int)
        inst_holders['% Out'] = inst_holders['% Out'] * 100
        display_df = inst_holders[['Holder', 'Shares', 'Date Reported', '% Out', 'Value (B$)']].copy()
        display_df['% Out'] = display_df['% Out'].apply(lambda x: f"{x:.2f}%")
        display_df['Shares'] = display_df['Shares'].apply(lambda x: f"{x:,.0f}")
        display_df['Value (B$)'] = display_df['Value (B$)'].apply(lambda x: f"{x:.2f}")
        st.dataframe(display_df, hide_index=True)
    else:
        st.write("Non disponible via yfinance pour ce symbole.")
except Exception as e:
    st.error(f"Erreur lors de la récupération des données actionnaires/initiés : {str(e)}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.3rem !important; }
[data-testid="stMetricLabel"] { opacity: 0.8; }
</style>
""", unsafe_allow_html=True)