import streamlit as st
from widgets.indices import show_indices
from widgets.trending import show_trending

# Configuration de la page
st.title("FinLite - Lightweight Financial Terminal")


# Affichage des widgets directement
show_indices()
show_trending()
# Pied de page
st.sidebar.write("""**Welcome to FinLite(lite Version)**"
This is a free, open-source demo built in Python, showcasing basic portfolio analysis with real-time data (~5-min delay). Explore a sample portfolio, track asset values, and visualize gains/losses. Designed for simplicity and hosted on Streamlit Community Cloud, this is just a taste of FinLite’s potential!
""")

# Footer
st.markdown("""
<div class="footer">
FinLite v1.0 (Lite) - Deployed on Streamlit Community Cloud - Make app with love ❤ orionDeimos 
</div>
""", unsafe_allow_html=True)