#!/usr/bin/python3
from api_connection.api_client import ApiClient
from indicators.bollinger_bands import BollingerBands
import plotly.graph_objs as go


def visualize(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color='black', width=1.5), name='Real Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Middle Band'], line=dict(color='blue', width=.7), name='Middle Band'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Lower Band'], line=dict(color='red', width=1), name='Lower Band'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Upper Band'], line=dict(color='green', width=1), name='Upper Band'))

    fig.update_layout(
        title='Bollinger Bands Strategy',
        yaxis_title='Price'
    )
    fig.show()


def main():
    
    client = ApiClient()
    client.connect()

    eth_balance = client.get_asset_balance(asset='ETH')
    print(eth_balance)

    balance = client.get_balance()

    for coin in balance:
        print(coin)

    r_client = client.get_raw_client()

    print(f'Ethereum price: {client.get_current_price(symbol="ETHUSDT")}')

    candles = client.get_candles(symbol='ETHUSDT', interval='1m')
    print(candles)

    close_prices = client.get_close_prices_dataframe(symbol='ETHUSDT', interval='1m')
    print(close_prices)

    bb = BollingerBands(close_prices)
    bb.initialize_indicator()
    bb_dataframe = bb.dataframe.dropna()
    print(bb_dataframe)

    visualize(bb_dataframe)


if __name__ == '__main__':
    main()

