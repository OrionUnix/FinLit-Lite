import streamlit as st
from widgets.indices import show_indices
from widgets.trending import show_trending
from widgets.fear import display_fear_greed_widget

# Configuration de la page
st.set_page_config(page_title="FinLite Dashboard", layout="wide")

# Titre principal avec style
st.markdown("""
    <h1 style='text-align: center; color: #333; font-family: Arial, sans-serif; margin-bottom: 20px;'>
        FinLite - Lightweight Financial Terminal
    </h1>
""", unsafe_allow_html=True)

# Disposition en colonnes pour les widgets
col1, col2 = st.columns([2, 1])

with col1:
    show_indices()

with col2:

    display_fear_greed_widget()

# Widget Trending en pleine largeur en dessous

show_trending()

# Sidebar optimisée
with st.sidebar:
    st.markdown("""
        <div style='font-family: Arial, sans-serif; padding: 10px;'>
            <h3 style='color: #333;'>Welcome to FinLite (Lite Version)</h3>
            <p style='color: #666; font-size: 0.9rem;'>
                This is a free, open-source demo built in Python, showcasing basic portfolio analysis with real-time data (~5-min delay). Explore a sample portfolio, track asset values, and visualize gains/losses. Designed for simplicity and hosted on Streamlit Community Cloud, this is just a taste of FinLite’s potential!
            </p>
            <p style='text-align: center; margin-top: 20px;'>
                <a href='/' style='color: #34C759; text-decoration: none;'>🏠 Home</a> | 
                <a href='/asset?symbol=NVDA' style='color: #34C759; text-decoration: none;'>📊 Asset</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

# Footer stylé avec transparence en thème sombre
st.markdown("""
    <style>
        /* Style général du footer */
        .footer {
            text-align: center;
            padding: 15px;
            border-top: 1px solid rgba(200, 200, 200, 0.2);
            color: #666;
            font-size: 0.9rem;
            position: fixed;
            bottom: 0;
            width: 100%;
            left: 0;
            background-color: rgba(249, 249, 249, 0.8); /* Fond clair semi-transparent par défaut */
        }

        /* Adaptation au thème sombre */
        [data-theme="dark"] .footer {
            background-color: rgba(0, 0, 0, 0.2); /* Fond sombre semi-transparent */
            color: #ccc;
            border-top: 1px solid rgba(200, 200, 200, 0.1);
        }

        /* Liens dans le footer */
        .footer a {
            color: #34C759;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }

        /* Responsivité */
        @media (max-width: 768px) {
            .footer {
                position: relative;
                margin-top: 20px;
            }
        }

        /* Adaptation des autres éléments au thème sombre */
        [data-theme="dark"] h1 {
            color: #ddd; /* Titre en clair pour thème sombre */
        }
        [data-theme="dark"] .sidebar h3 {
            color: #ddd; /* Titre sidebar en clair */
        }
        [data-theme="dark"] .sidebar p {
            color: #bbb; /* Texte sidebar en gris clair */
        }
        [data-theme="dark"] hr {
            border-color: rgba(200, 200, 200, 0.2); /* Ligne en thème sombre */
        }
    </style>
    <div class="footer">
        FinLite v1.0 (Lite) - Deployed on <a href="https://streamlit.io/cloud" target="_blank">Streamlit Community Cloud</a> - Made with ❤ by orionDeimos
    </div>
""", unsafe_allow_html=True)