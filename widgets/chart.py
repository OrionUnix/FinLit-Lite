import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

def create_price_chart(df, symbol, name, chart_type='Candlesticks', show_volume=True, show_bollinger=False, show_ema=False, show_rsi=False, show_macd=False, show_fibo=False, theme_colors=None):
    colors = {
        'primary': '#57d5b9',
        'secondary': '#6a6c79',
        'positive': '#50a394',
        'negative': '#c1467f',
        'background': '#1a1a1a',
        'grid': '#2d2d36',
        'volume': 'rgba(100, 100, 100, 0.15)',
        'text': '#ffffff'
    }
    if theme_colors:
        colors.update(theme_colors)
    
    fig = go.Figure()
    try:
        _validate_data(df)
        df = df.copy()

        if show_bollinger:
            df = _add_bollinger_bands(df)
        
        _add_main_chart(fig, df, chart_type, colors)
        if show_volume:
            _add_volume(fig, df, colors)
        if show_bollinger:
            _plot_bollinger_bands(fig, df, colors)

        _configure_layout(fig, df, symbol, name, colors, show_fibo)

    except Exception as e:
        fig = _handle_error(fig, e)

    return fig

def _validate_data(df):
    required = ['Open', 'High', 'Low', 'Close']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes : {', '.join(missing)}")

def _add_main_chart(fig, df, chart_type, colors):
    if chart_type == 'Candlesticks':
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Prix', increasing_line_color=colors['positive'], decreasing_line_color=colors['negative']))
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=colors['primary'], width=1.5), name='Prix'))

def _add_bollinger_bands(df):
    bb = ta.bbands(df['Close'], length=20)
    return pd.concat([df, bb], axis=1).dropna()

def _plot_bollinger_bands(fig, df, colors):
    fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], line=dict(color=colors['grid'], width=1), name='Bollinger Up'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], fill='tonexty', line=dict(color=colors['grid'], width=1), name='Bollinger Low'))

def _add_volume(fig, df, colors):
    if 'Volume' in df.columns:
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker=dict(color=colors['volume']), yaxis='y2'))

def _configure_layout(fig, df, symbol, name, colors, show_fibo):
    fig.update_layout(
        height=600, template="plotly_dark", plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font=dict(color=colors['text'], size=12),
        margin=dict(t=60, b=40, l=60, r=40),
        xaxis=dict(rangeselector=dict(buttons=[dict(count=1, label="1D", step="day"), dict(count=5, label="5D", step="day"), dict(count=1, label="1M", step="month"), dict(count=5, label="5M", step="month"), dict(count=1, label="1Y", step="year"), dict(count=2, label="2Y", step="year"), dict(count=5, label="5Y", step="year")], bgcolor=colors['background'], activecolor=colors['primary'], bordercolor=colors['grid'], borderwidth=1, font=dict(color=colors['text'], size=10)), rangeslider=dict(visible=True), type="date"),
        yaxis=dict(title="Prix ($)", gridcolor=colors['grid'], side='left'),
        yaxis2=dict(title="Volume", overlaying='y', side='right', showgrid=False),
        legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=0.98),
        annotations=[dict(text=f"FinLite - {name} ({symbol})", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(size=20, color=colors['text']))]
    )

def _handle_error(fig, error):
    print(f"Erreur : {str(error)}")
    return fig.add_annotation(text="Erreur de chargement", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)