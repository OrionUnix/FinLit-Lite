# FinLite - Lightweight Financial Terminal (Demo)

FinLite is a free, open-source financial terminal built in Python, designed as a lightweight demo for portfolio analysis and market indices tracking. This version is optimized for deployment on Streamlit Community Cloud.

## Explore the App

If you'd like to see what it looks like, feel free to visit my page: [FinLit Lite App](https://finlit.streamlit.app/)


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
   ```bash 
   pip install -r requirements.txt
3. Run locally
  ```bash
streamlit run app.py

```bash
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
    │   technical_chart.py        # Price chart advance technique"# FinLit-Lite" 
    │   fear.py        # fear and gread calcul indice"# FinLit-Lite" 

**Created by: OrionDeimos**