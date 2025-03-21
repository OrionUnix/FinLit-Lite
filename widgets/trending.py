import streamlit as st
import yfinance as yf
import pandas as pd

# Liste statique de symboles par marché avec noms et secteurs
MARKETS = {
    "US": [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Communication Services"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services"},
    ],
    "Europe": [
        {"symbol": "VOW3.DE", "name": "Volkswagen AG", "sector": "Consumer Cyclical"},
        {"symbol": "SAP.DE", "name": "SAP SE", "sector": "Technology"},
        {"symbol": "ASML.AS", "name": "ASML Holding N.V.", "sector": "Technology"},
        {"symbol": "MC.PA", "name": "LVMH Moët Hennessy", "sector": "Consumer Cyclical"},
        {"symbol": "SAN.PA", "name": "Sanofi", "sector": "Healthcare"},
    ],
    "Asia": [
        {"symbol": "0700.HK", "name": "Tencent Holdings Ltd.", "sector": "Communication Services"},
        {"symbol": "9988.HK", "name": "Alibaba Group Holding Ltd.", "sector": "Consumer Cyclical"},
        {"symbol": "9618.HK", "name": "JD.com Inc.", "sector": "Consumer Cyclical"},
        {"symbol": "005930.KS", "name": "Samsung Electronics Co.", "sector": "Technology"},
        {"symbol": "6501.T", "name": "Hitachi Ltd.", "sector": "Industrials"},
    ],
    "Crypto": [
        {"symbol": "BTC-USD", "name": "Bitcoin", "sector": "Cryptocurrency"},
        {"symbol": "AVAX-USD", "name": "Avalanche", "sector": "Cryptocurrency"},
        {"symbol": "BNB-USD", "name": "Binance Coin", "sector": "Cryptocurrency"},
    ],
    "Commodities": [
        {"symbol": "GC=F", "name": "Gold Futures", "sector": "Commodities"},
        {"symbol": "SI=F", "name": "Silver Futures", "sector": "Commodities"},
        {"symbol": "CL=F", "name": "Crude Oil Futures", "sector": "Commodities"},
    ]
}

@st.cache_data(ttl=1800)
def fetch_market_data(market: str):
    """Récupère les données pour tous les symboles d’un marché."""
    assets = MARKETS.get(market, [])
    if not assets:
        return pd.DataFrame()
    symbols = [asset["symbol"] for asset in assets]
    try:
        data = yf.download(symbols, period="7d", interval="1d", progress=False)
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
    """Affiche les top gainers et losers par marché avec st.metric."""
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
            for asset in MARKETS[market]:
                change, amount, price = calculate_performance(close_data, asset["symbol"])
                if change is not None:
                    performances.append({
                        "symbol": asset["symbol"],
                        "name": asset["name"],
                        "sector": asset["sector"],
                        "change": change,
                        "amount_change": amount,
                        "price": price,
                        "volume": None  # Volume non inclus pour l'instant
                    })

            if not performances:
                st.write("No performance data available")
                continue

            # Tri pour top gainers et losers
            sorted_perf = sorted(performances, key=lambda x: x["change"], reverse=True)
            top_gainers = sorted_perf[:2]
            top_losers = sorted_perf[-2:][::-1]

            # Couleurs par défaut de Streamlit
            positive_color = "#34C759"  # Vert
            negative_color = "#FF4B4B"  # Rouge (primaryColor)

            # Affichage dans un container
            with st.container():
                st.write("**Top Gainers**")
                cols = st.columns(2)
                for idx, asset in enumerate(top_gainers):
                    with cols[idx]:
                        # Header avec symbole cliquable
                        st.markdown(
                            f"<a href='/asset?symbol={asset['symbol']}' style='text-decoration: none; color: inherit;'><div style='text-align: center; font-weight: bold; font-size: 1.1rem; padding: 5px;'>{asset['symbol']}</div></a>",
                            unsafe_allow_html=True
                        )
                        # Metric avec fond coloré
                        background_color = positive_color if asset['change'] >= 0 else negative_color
                        st.markdown(
                            f"<div style='background-color: {background_color}; border-radius: 5px; padding: 10px;'>",
                            unsafe_allow_html=True
                        )
                        st.metric(
                            label=f"{asset['name']} ({asset['sector']})",
                            value=f"{asset['price']:,.2f}$",
                            delta=f"{'▲' if asset['change'] >= 0 else '▼'} {abs(asset['change']):.2f}% ({asset['amount_change']:+.2f}$)",
                            delta_color="normal" if asset['change'] >= 0 else "inverse",
                            border=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                st.write("**Top Losers**")
                cols = st.columns(2)
                for idx, asset in enumerate(top_losers):
                    with cols[idx]:
                        # Header avec symbole cliquable
                        st.markdown(
                            f"<a href='/asset?symbol={asset['symbol']}' style='text-decoration: none; color: inherit;'><div style='text-align: center; font-weight: bold; font-size: 1.1rem; padding: 5px;'>{asset['symbol']}</div></a>",
                            unsafe_allow_html=True
                        )
                        # Metric avec fond coloré
                        background_color = positive_color if asset['change'] >= 0 else negative_color
                        st.markdown(
                            f"<div style='background-color: {background_color}; border-radius: 5px; padding: 10px;'>",
                            unsafe_allow_html=True
                        )
                        st.metric(
                            label=f"{asset['name']} ({asset['sector']})",
                            value=f"{asset['price']:,.2f}$",
                            delta=f"{'▲' if asset['change'] >= 0 else '▼'} {abs(asset['change']):.2f}% ({asset['amount_change']:+.2f}$)",
                            delta_color="normal" if asset['change'] >= 0 else "inverse",
                            border=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    show_trending()