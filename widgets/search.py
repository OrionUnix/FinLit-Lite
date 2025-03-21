import streamlit as st

def show_search():
    """Display a search module for assets."""
    st.markdown("### Search for an Asset")
    search_query = st.text_input("Enter a symbol or company name (e.g., AAPL, Google):", "")
    if search_query:
        st.query_params["symbol"] = search_query.upper()
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    show_search()