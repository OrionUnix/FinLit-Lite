import streamlit as st
import yfinance as yf
import pandas as pd

# Liste statique de symboles par marché
MARKETS = {
    "US": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM"],
    "Europe": ["VOW3.DE", "SAP.DE", "ASML.AS", "MC.PA", "SAN.PA"],
    "Asia": ["0700.HK", "9988.HK", "9618.HK", "005930.KS", "6501.T"]
}

@st.cache_data(ttl=1800)
def fetch_market_data(market: str):
    symbols = MARKETS.get(market, [])
    if not symbols:
        return pd.DataFrame()
    try:
        data = yf.download(symbols, period="7d", interval="1d", progress=False)  # Changé de 2d à 7d
        if data.empty or data["Close"].isna().all().all():
            st.warning(f"No data returned for {market}.")
            return pd.DataFrame()
        return data["Close"]
    except Exception as e:
        st.error(f"Erreur récupération données {market}: {str(e)}")
        return pd.DataFrame()

def calculate_performance(close_data, symbol):
    """Calcule la performance journalière pour un symbole."""
    if symbol not in close_data.columns or len(close_data[symbol].dropna()) < 2:
        return None, None, None
    yesterday = close_data[symbol].iloc[-2]
    today = close_data[symbol].iloc[-1]
    if pd.isna(yesterday) or pd.isna(today):
        return None, None, None
    change_percent = ((today - yesterday) / yesterday) * 100
    amount_change = today - yesterday
    return change_percent, amount_change, today

def show_trending():
    """Affiche les top gainers et losers par marché dans des cartes avec CSS."""
    st.subheader("Trending Stocks")

    # Onglets pour chaque marché
    tab_names = list(MARKETS.keys())
    tabs = st.tabs(tab_names)

    for i, tab in enumerate(tabs):
        with tab:
            market = tab_names[i]
            close_data = fetch_market_data(market)
            
            if close_data.empty:
                st.write(f"No data available for {market}")
                continue

            # Calcul des performances
            performances = []
            for symbol in MARKETS[market]:
                change, amount, price = calculate_performance(close_data, symbol)
                if change is not None:
                    performances.append({
                        "symbol": symbol,
                        "name": symbol,
                        "change": change,
                        "amount_change": amount,
                        "price": price,
                        "volume": None
                    })

            if not performances:
                st.write("No performance data available")
                continue

            # Tri pour top gainers et losers
            sorted_perf = sorted(performances, key=lambda x: x["change"], reverse=True)
            top_gainers = sorted_perf[:2]
            top_losers = sorted_perf[-2:][::-1]

            # Affichage dans un container
            with st.container():
                st.write("**Top Gainers**")
                cols = st.columns(2)
                for idx, asset in enumerate(top_gainers):
                    with cols[idx]:
                        border_color = "#34C759" if asset['change'] >= 0 else "#FF4C52"  # Vert ou rouge
                        st.markdown(
                            f"""
                            <div style="border: 2px solid {border_color}; border-radius: 5px; padding: 10px;">
                                <a href="/asset?symbol={asset['symbol']}">{asset['symbol']}</a><br>
                                Price: {asset['price']:,.2f}$<br>
                                <span style="color: {'#34C759' if asset['change'] >= 0 else '#FF4C52'}">
                                    {'▲' if asset['change'] >= 0 else '▼'} {abs(asset['change']):.2f}%
                                </span><br>
                                Amount: {asset['amount_change']:+.2f}$
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.write("**Top Losers**")
                cols = st.columns(2)
                for idx, asset in enumerate(top_losers):
                    with cols[idx]:
                        border_color = "#34C759" if asset['change'] >= 0 else "#FF4C52"  # Vert ou rouge
                        st.markdown(
                            f"""
                            <div style="border: 2px solid {border_color}; border-radius: 5px; padding: 10px;">
                                <a href="/asset?symbol={asset['symbol']}">{asset['symbol']}</a><br>
                                Price: {asset['price']:,.2f}$<br>
                                <span style="color: {'#34C759' if asset['change'] >= 0 else '#FF4C52'}">
                                    {'▲' if asset['change'] >= 0 else '▼'} {abs(asset['change']):.2f}%
                                </span><br>
                                Amount: {asset['amount_change']:+.2f}$
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    show_trending()