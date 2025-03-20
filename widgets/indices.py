import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import datetime

# Configuration des marchés et indices avec heures d'ouverture (en UTC)
MARCHES = {
    "US": {
        "^GSPC": {"name": "S&P 500", "position": 0, "open_utc": (13, 30), "close_utc": (20, 0)},  # 9h30-16h EST
        "^DJI": {"name": "Dow Jones", "position": 1, "open_utc": (13, 30), "close_utc": (20, 0)},
        "^IXIC": {"name": "Nasdaq", "position": 2, "open_utc": (13, 30), "close_utc": (20, 0)}
    },
    "Europe": {
        "^STOXX50E": {"name": "Euro Stoxx 50", "position": 0, "open_utc": (8, 0), "close_utc": (16, 30)},  # 9h-17h30 CET
        "^FTSE": {"name": "FTSE 100", "position": 1, "open_utc": (8, 0), "close_utc": (16, 30)},  # 8h-16h30 GMT
        "^GDAXI": {"name": "DAX", "position": 2, "open_utc": (8, 0), "close_utc": (16, 30)}  # 9h-17h30 CET
    },
    "Asia": {
        "000001.SS": {"name": "SSE Compo", "position": 0, "open_utc": (1, 30), "close_utc": (7, 0)},  # 9h30-15h CST
        "^N225": {"name": "Nikkei 225", "position": 1, "open_utc": (0, 0), "close_utc": (6, 0)},  # 9h-15h JST
        "^HSI": {"name": "Hang Seng", "position": 2, "open_utc": (1, 30), "close_utc": (8, 0)}  # 9h30-16h HKT
    },
    "Commodities": {
        "CL=F": {"name": "Crude Oil", "position": 0, "open_utc": (0, 0), "close_utc": (23, 59)},  # 24h approx
        "GC=F": {"name": "Gold Future", "position": 1, "open_utc": (0, 0), "close_utc": (23, 59)},
        "SI=F": {"name": "Silver", "position": 2, "open_utc": (0, 0), "close_utc": (23, 59)}
    },
    "Crypto": {
        "BTC-USD": {"name": "BTC", "position": 0, "open_utc": (0, 0), "close_utc": (23, 59)},  # 24h
        "BNB-USD": {"name": "BNB", "position": 1, "open_utc": (0, 0), "close_utc": (23, 59)},
        "ETH-USD": {"name": "ETH", "position": 2, "open_utc": (0, 0), "close_utc": (23, 59)}
    },
    "Currencies": {
        "EURUSD=X": {"name": "EUR/USD", "position": 0, "open_utc": (0, 0), "close_utc": (23, 59)},  # 24h
        "USDJPY=X": {"name": "USD/JPY", "position": 1, "open_utc": (0, 0), "close_utc": (23, 59)},
        "GBPUSD=X": {"name": "USD/GBP", "position": 2, "open_utc": (0, 0), "close_utc": (23, 59)}
    }
}

@st.cache_data(ttl=300)  # Cache de 5 minutes
def get_indices_data(market: str):
    """Récupère les données des indices pour un marché donné."""
    indices = MARCHES.get(market, {})
    symbols = list(indices.keys())
    try:
        data = yf.download(symbols, period="5d", interval="1h", progress=False)
        if data.empty:
            st.warning(f"No data returned for {market}.")
        return data
    except Exception as e:
        st.error(f"Error fetching data for {market}: {str(e)}")
        return pd.DataFrame()

def is_market_open(symbol: str, current_time: datetime.datetime) -> bool:
    """Vérifie si le marché est ouvert en fonction de l’heure UTC actuelle."""
    market_info = next((info for market in MARCHES.values() for s, info in market.items() if s == symbol), None)
    if not market_info:
        return True  # Par défaut, considère ouvert si pas d’info

    open_hour, open_minute = market_info["open_utc"]
    close_hour, close_minute = market_info["close_utc"]
    
    open_time = datetime.time(open_hour, open_minute)
    close_time = datetime.time(close_hour, close_minute)
    current_time_utc = current_time.time()
    
    if open_time < close_time:
        return open_time <= current_time_utc <= close_time
    else:  # Cas où le marché traverse minuit (peu probable ici)
        return current_time_utc >= open_time or current_time_utc <= close_time

def render_index_cards(market: str):
    """Affiche les cartes des indices en 3 colonnes avec statut du marché."""
    data = get_indices_data(market)
    indices = MARCHES[market]
    current_time = datetime.datetime.now(datetime.UTC)  # Heure actuelle en UTC
    
    if data.empty:
        st.write("No data available for this market.")
        return
    
    cols = st.columns(3)
    for i, (symbol, details) in enumerate(indices.items()):
        with cols[i]:
            try:
                if not is_market_open(symbol, current_time):
                    st.write(f"**{details['name']}**: Market closed")
                elif symbol in data["Close"] and not data["Close"][symbol].isna().all():
                    current = data["Close"][symbol].iloc[-1]
                    prev_close = data["Close"][symbol].iloc[-2]
                    if pd.isna(current) or pd.isna(prev_close):
                        st.write(f"**{details['name']}**: Insufficient data")
                    else:
                        change_percent = ((current - prev_close) / prev_close) * 100
                        trend = "▲" if change_percent >= 0 else "▼"
                        st.write(f"**{details['name']}**")
                        st.write(f"Current: ${current:,.2f}")
                        st.write(f"Change: {trend} {abs(change_percent):.2f}%")
                        st.write(f"Previous: ${prev_close:,.2f}")
                else:
                    st.write(f"**{details['name']}**: Data unavailable")
            except Exception as e:
                st.write(f"**{details['name']}**: Error - {str(e)}")

def render_line_chart(market: str):
    """Affiche un graphique en ligne des évolutions en pourcentage dans un container."""
    data = get_indices_data(market)
    indices = MARCHES[market]

    if data.empty:
        st.warning("No data available for the chart.")
        return

    data_frames = []
    for symbol, details in indices.items():
        if symbol in data["Close"] and not data["Close"][symbol].isna().all():
            hist = pd.DataFrame({"Close": data["Close"][symbol]}).reset_index()
            hist = hist.rename(columns={"Date": "Datetime"})  # Standardisation
            initial_value = hist["Close"].iloc[0]
            if pd.notna(initial_value):
                hist["Percent_Change"] = ((hist["Close"] - initial_value) / initial_value) * 100
                hist["Name"] = details["name"]
                data_frames.append(hist)

    if data_frames:
        combined_df = pd.concat(data_frames)
        with st.container():
            fig = px.line(
                combined_df,
                x="Datetime",
                y="Percent_Change",
                color="Name",
                title=f"{market} Indices - 1 Day Performance",
                labels={"Percent_Change": "Change (%)", "Datetime": "Time"}
            )
            fig.update_layout(yaxis_ticksuffix="%")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No valid data available for the chart.")

def show_indices():
    """Point d’entrée du widget avec onglets."""
    st.subheader("Market Indices")
    
    tab_names = list(MARCHES.keys())
    tabs = st.tabs(tab_names)
    
    for i, tab in enumerate(tabs):
        with tab:
            market = tab_names[i]
            render_index_cards(market)
            render_line_chart(market)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    show_indices()