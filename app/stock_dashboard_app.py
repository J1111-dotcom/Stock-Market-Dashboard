import dash
from dash import dcc, html
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

#Initializing the app
app = dash.Dash(__name__)
server = app.server #For deployment compatibility

#Define stock symbols and labels
tickers = {
    'Tesla' : 'TSLA',
    'Amazon' : 'AMZN',
    'AMD' : 'AMD',
    'GameStop' : 'GME'
}

#App Layout
app.layout = html.Div(
    style={'maxWidth': '800px', 'margin': 'auto', 'padding': '20px'},
    children=[
    html.H1("Stock Market Dashboard", style={'textAlign': 'center'}),

    html.Div([
    html.Label("Select a stock", style={'fontWeight': 'bold'}),
    dcc.Dropdown(
        id="stock-selector",
        options=[{'label': name, 'value': symbol} for name, symbol in tickers.items()],
        value='AMZN', #defalut value
        style={'marginBottom': '20px'}
    ),
    ]),

    html.Div(id='kpi-container', style={'marginBottom': '40px'}),

    dcc.Graph(id='stock-graph')
])

#Callback function to update graph based on selected stock

from dash.dependencies import Input, Output

@app.callback(
    Output('stock-graph', 'figure'),
    Output('kpi-container', 'children'),
    Input('stock-selector', 'value')
)
def update_dashboard(selected_symbol):
    df = yf.Ticker(selected_symbol).history(period="5y")
    df.reset_index(inplace=True)

    if df.empty:
        return go.Figure(), "No data available."

    # Calculate KPIs
    latest_close = df['Close'].iloc[-1]
    start_close = df['Close'].iloc[0]
    pct_return = ((latest_close - start_close) / start_close) * 100
    highest_close = df['Close'].max()

    # Format KPIs
    kpi_layout = html.Div([
        html.Div(f"Latest Close: ${latest_close:.2f}", style={'marginBottom': '8px'}),
        html.Div(f"5-Year Return: {pct_return:.2f}%", style={'marginBottom': '8px'}),
        html.Div(f"Highest Close: ${highest_close:.2f}")
    ], style={'fontWeight': 'bold', 'fontSize': '18px'})

    # Graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Open'], mode='lines', name='Open'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))

    fig.update_layout(
        title=f"{selected_symbol} Stock Prices (Open vs Close)",
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_white'
    )

    return fig, kpi_layout


if __name__ == '__main__':
    app.run(debug=True)