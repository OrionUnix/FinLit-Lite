import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Asset Details", layout="wide")

# Couleurs par défaut de Streamlit
positive_color = "#34C759"  # Vert
negative_color = "#FF4B4B"  # Rouge (primaryColor)

@st.cache_data(ttl=3600, show_spinner="Loading asset data...")
def get_asset_data(symbol):
    """Retrieve asset data via yfinance."""
    try:
        asset = yf.Ticker(symbol)
        return {
            "info": asset.info,
            "history": asset.history(period="1y", interval="1d"),
            "financials": asset.financials,
            "cashflow": asset.cashflow,
            "dividends": asset.dividends
        }
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
        st.stop()

def create_price_chart(df, chart_type="Candlestick"):
    """Create a price chart (Line or Candlestick)."""
    fig = go.Figure()
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            increasing_line_color=positive_color,
            decreasing_line_color=negative_color
        ))
    else:  # Line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            line=dict(color=positive_color),
            name="Price"
        ))
    fig.update_layout(
        title="Price History (1 Year)",
        yaxis_title="Price ($)",
        xaxis_title="Date",
        template="plotly_white",
        margin=dict(t=40, b=20),
        height=400
    )
    return fig

def calculate_technical(df):
    """Calculate RSI and MACD technical indicators."""
    try:
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        return pd.concat([df, macd], axis=1)
    except Exception as e:
        st.error(f"Error calculating indicators: {str(e)}")
        return df

# Sidebar
with st.sidebar:
    st.markdown("""
    ### Welcome to FinLite (Lite Version)  
    This is a free, open-source demo built in Python, showcasing basic portfolio analysis with real-time data (~5-min delay). Explore a sample portfolio, track asset values, and visualize gains/losses. Designed for simplicity and hosted on Streamlit Community Cloud, this is just a taste of FinLite’s potential!
    """)
    st.markdown(f"- 🏠 [Home](/)", unsafe_allow_html=True)
    st.markdown(f"- 📊 [Asset](/asset?symbol={st.query_params.get('symbol', 'AAPL')})", unsafe_allow_html=True)

# Récupération des données
symbol = st.query_params.get("symbol", "META")  # Par défaut META
asset_data = get_asset_data(symbol)
info = asset_data["info"]
history = asset_data["history"]

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

        # Carte principale
        background_color = positive_color if change_pct >= 0 else negative_color
        st.markdown(
            f"""
            <div class='asset-card' style='border-radius: 10px; border: 1px solid #ccc; background: transparent; padding: 0;'>
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

        # Key Metrics mis à jour
        st.subheader("Key Metrics")
        st.markdown(
            f"""
            <div style='padding: 0.5rem; border: 1px solid #ccc; border-radius: 5px; background: transparent;'>
                <div style='font-size: 0.9rem;'>Previous Close: {info.get('regularMarketPreviousClose', 'N/A')}$</div>
                <div style='font-size: 0.9rem;'>Open: {info.get('regularMarketOpen', 'N/A')}$</div>
                <div style='font-size: 0.9rem;'>Bid: {bid}$</div>
                <div style='font-size: 0.9rem;'>Earnings Date: Apr 22, 2025 - Apr 28, 2025</div>
                <div style='font-size: 0.9rem;'>Dividend & Yield: 2.10 (0.36%)</div>
                <div style='font-size: 0.9rem;'>Ex-Dividend Date: Mar 14, 2025</div>
                <div style='font-size: 0.9rem;'>1y Target Est: {info.get('targetMeanPrice', 'N/A')}$</div>
                <div style='font-size: 0.9rem;'>Market Cap (Intraday): {info.get('marketCap', 0)/1e9:.2f}B$</div>
                <div style='font-size: 0.9rem;'>Sector: {info.get('sector', 'N/A')}</div>
                <div style='font-size: 0.9rem;'>Beta: {info.get('beta', 'N/A')}</div>
                <div style='font-size: 0.9rem;'>PE Ratio: {info.get('trailingPE', 'N/A')}</div>
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
        fig = create_price_chart(history, chart_type=chart_type)
        st.plotly_chart(fig, use_container_width=True, config={
            "displayModeBar": True,
            "modeBarButtonsToAdd": ["drawline", "drawrect", "eraseshape"]
        })
    except Exception as e:
        st.error(f"Error displaying chart: {str(e)}")

# Analyse Technique Avancée (RSI et MACD)
st.subheader("Advanced Technical Analysis")
try:
    df = calculate_technical(history)
    col1, col2 = st.columns(2)
    with col1:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color=positive_color), name="RSI"))
        fig_rsi.update_layout(title="RSI (14 days)", yaxis_title="RSI", height=300, showlegend=False, template="plotly_white")
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        st.plotly_chart(fig_rsi, use_container_width=True)
    with col2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], line=dict(color=positive_color), name="MACD"))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], line=dict(color=negative_color), name="Signal"))
        fig_macd.update_layout(title="MACD (12/26/9)", yaxis_title="MACD", height=300, template="plotly_white")
        st.plotly_chart(fig_macd, use_container_width=True)
except Exception as e:
    st.error(f"Error in technical analysis: {str(e)}")

# Analyse Fondamentale
try:
    st.subheader("Fundamental Analysis")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Valuation", "Finances", "Dividends", "Competitors", "Performance Overview"])

    with tab1:
        valuation_data = {
            "P/E": asset_data['info'].get('trailingPE', 'N/A'),
            "P/S": asset_data['info'].get('priceToSalesTrailing12Months', 'N/A'),
            "EV/EBITDA": asset_data['info'].get('enterpriseToEbitda', 'N/A'),
            "P/B": asset_data['info'].get('priceToBook', 'N/A'),
            "Dividend Yield": f"{asset_data['info'].get('dividendYield', 0)*100:.2f}%",
            "Beta (5Y Monthly)": asset_data['info'].get('beta', 'N/A'),
            "EPS (TTM)": asset_data['info'].get('trailingEps', 'N/A')
        }
        st.table(pd.DataFrame(valuation_data.items(), columns=["Ratio", "Value"]))

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
        st.metric("Dividend Yield", f"{asset_data['info'].get('dividendYield', 0)*100:.2f}%", f"Payout Ratio: {asset_data['info'].get('payoutRatio', 'N/A')}")
        if asset_data['dividends'] is not None and not asset_data['dividends'].empty:
            st.write("### Dividend History (Last 5 Years)")
            five_years_ago = datetime.now().year - 5
            div_history = asset_data['dividends'][asset_data['dividends'].index.year >= five_years_ago]
            if not div_history.empty:
                st.table(div_history.rename("Dividend ($)").to_frame())
            else:
                st.write("No dividends paid in the last 5 years.")
        else:
            st.write("No dividend history available.")

    with tab4:
        st.write("### Major Competitors")
        st.write("This is a Lite/Demo version. Competitor data is not available in this release.")
        st.write("Here are some potential competitors based on sector:")
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
            "META": ["0.17%", "16.34%", "171.96%", "293.22%"],
            "S&P 500 (^GSPC)": ["3.72%", "8.39%", "26.88%", "145.69%"]
        }
        st.table(pd.DataFrame(performance_data))

except Exception as e:
    st.error(f"Error in fundamental analysis: {str(e)}")

# DCF Valuation
st.subheader("DCF Valuation")
st.write("""
### Discounted Cash Flow (DCF) Analysis
Estimate the intrinsic value of the asset by adjusting the sliders below. The DCF model calculates the present value of future cash flows based on your inputs for Free Cash Flow (FCF) growth rate, discount rate, and terminal growth rate.
""")
try:
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
            current_mc = asset_data['info'].get('marketCap', 0)
            delta = dcf_value - current_mc
            st.metric("Estimated DCF Value", f"{dcf_value/1e9:.2f}B$", delta=f"{delta/1e9:.2f}B$ vs Market Cap", delta_color="normal" if delta > 0 else "inverse")
        else:
            st.warning("Discount rate must be greater than terminal growth rate")
    else:
        st.warning("Cash flow data not available")

    # Graphique des revenus et bénéfices
    st.write("### Revenue and Earnings (Q1-Q4 2024)")
    revenue_data = {
        "Quarter": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
        "Revenue (B$)": [36.45, 39.07, 40.59, 48.39],  # Valeurs réelles ou estimées
        "Earnings (EPS)": [4.71, 5.16, 6.03, 8.02]
    }
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=revenue_data["Quarter"], y=revenue_data["Revenue (B$)"], name="Revenue (B$)", marker_color=positive_color))
    fig_bar.add_trace(go.Bar(x=revenue_data["Quarter"], y=revenue_data["Earnings (EPS)"], name="Earnings (EPS)", marker_color=negative_color))
    fig_bar.update_layout(barmode='group', title="Revenue and Earnings by Quarter (2024)", height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Estimations
    st.write("### Earnings Estimates")
    earnings_estimates = {
        "Metric": ["No. of Analysts", "Avg. Estimate", "Low Estimate", "High Estimate", "Prior Year EPS"],
        "Current Qtr (Mar 2025)": [44, 5.24, 4.7, 5.84, 4.71],
        "Next Qtr (Jun 2025)": [42, 5.79, 4.96, 6.33, 5.16],
        "Current Year (2025)": [60, 25.17, 21.18, 27.56, 23.86],
        "Next Year (2026)": [56, 28.8, 22.11, 33.39, 25.17]
    }
    st.table(pd.DataFrame(earnings_estimates))

    st.write("### Revenue Estimates")
    revenue_estimates = {
        "Metric": ["No. of Analysts", "Avg. Estimate", "Low Estimate", "High Estimate", "Prior Year Sales"],
        "Current Qtr (Mar 2025)": [45, "41.45B", "40.38B", "42.72B", "36.45B"],
        "Next Qtr (Jun 2025)": [45, "44.85B", "43.48B", "46.23B", "39.07B"],
        "Current Year (2025)": [62, "188.51B", "182.81B", "197.18B", "164.5B"],
        "Next Year (2026)": [58, "214.48B", "204.21B", "240.61B", "188.51B"]
    }
    st.table(pd.DataFrame(revenue_estimates))

except Exception as e:
    st.error(f"Error in DCF calculation: {str(e)}")

# Actionnaires et Initiés
st.subheader("Shareholders and Insiders")
try:
    st.write("### Major Shareholders")
    shareholders = {
        "Holder": ["Vanguard Group Inc", "Blackrock Inc", "FMR, LLC", "State Street Corporation", "JPMorgan Chase & Co"],
        "Shares": ["191.2M", "164.63M", "136.25M", "86.13M", "51.69M"],
        "Date Reported": ["Dec 31, 2024"]*5,
        "% Out": ["8.73%", "7.52%", "6.22%", "3.93%", "2.36%"],
        "Value": ["112.04B", "96.48B", "79.84B", "50.47B", "30.29B"]
    }
    st.table(pd.DataFrame(shareholders))

    st.write("### Insider Holdings (Last 24 Months - SEC Forms 3 & 4)")
    insiders = {
        "Name": ["Aaron Anderson", "John Douglas Arnold", "Andrew Bosworth", "Christopher K Cox", "Susan J. Li"],
        "Role": ["Officer", "Director", "Chief Technology Officer", "Officer", "Chief Financial Officer"],
        "Last Transaction": ["Conversion", "Conversion", "Sale", "Sale", "Sale"],
        "Date": ["Feb 14, 2025", "Feb 14, 2025", "Feb 14, 2025", "Feb 28, 2025", "Feb 14, 2025"],
        "Shares Held": ["4,304", "924", "77,650", "--", "--"]
    }
    st.table(pd.DataFrame(insiders))

except Exception as e:
    st.error(f"Error in shareholders/insiders: {str(e)}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
}
[data-testid="stMetricLabel"] {
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)