# FinLite - Lightweight Financial Terminal (Demo)

FinLite is a free, open-source financial terminal built in Python, designed as a lightweight demo for portfolio analysis and market indices tracking. This version is optimized for deployment on Streamlit Community Cloud.

## Features
- **Portfolio Analysis**: Track a demo portfolio with real-time data (~5-min delay) from Yahoo Finance.
- **Market Indices**: View major indices (US, Europe, Asia, etc.) with hourly updates and performance charts.
- **Lightweight**: No custom styles, minimal dependencies, and a small demo CSV.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FinLite.git
   cd FinLite
2. Install dependencies:
    pip install -r requirements.txt
3. Run locally
    streamlit run app.py

**Created by: OrionDeimos**

FinLite/
│   app.py              # Main entry point
│   requirements.txt    # Dependencies
│   README.md           # Documentation
│
└───pages/
│   │   asset.py        # Asset details page
│
└───widgets/
    │   indices.py      # Market indices widget
    │   trending.py     # Trending stocks widget
    │   chart.py        # Price chart utilities"# FinLit-Lite" 
