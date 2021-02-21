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


def bollinger_bands_strategy_example(dataframe):
    bb = BollingerBands(dataframe)
    bb.std_spacing = 1.96
    bb.initialize_indicator()
    bb_dataframe = bb.dataframe.dropna()
    print(bb_dataframe)

    print(bb.action_expedience())


def bollinger_bands_example(close_prices, plot=True):
    bb = BollingerBands(close_prices)
    bb.std_spacing = 1.96
    bb.initialize_indicator()
    bb_dataframe = bb.dataframe.dropna()
    print(bb_dataframe)

    bought = False

    init_money = 100

    money = init_money
    crypto_amount = 0
    for i, entry in bb_dataframe.iterrows():
        if entry['Close'] < entry['Lower Band']:
            if not bought:
                print(f"Start buying from price {entry['Close']}")
                bought = True
            if money > 0:
                crypto_amount = money / entry['Close']
                money = 0
                print(f"Buy at index {i}, price {entry['Close']}, Lower Band {entry['Lower Band']}")
        if entry['Close'] > entry['Upper Band']:
            if crypto_amount > 0:
                money = entry['Close'] * crypto_amount
                crypto_amount = 0
                print(f"Sell at index {i}, price {entry['Close']}, Upper Band {entry['Upper Band']}")
        i += 1

    if money > 0:
        print(f"Started with {init_money} and finished with {money}")
    else:
        print(f"Started with {init_money} and finished with {crypto_amount * bb_dataframe['Close'].iloc[-1]}")

    if plot:
        visualize(bb_dataframe)


def main():
    client = ApiClient()
    client.connect()
    dataframe = client.get_candles_dataframe(symbol='ETHUSDT', interval='1m')[['Close', 'Volume']]
    print(dataframe.head())
    bollinger_bands_strategy_example(dataframe)


def main2():
    
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

    bollinger_bands_example(close_prices, plot=False)

    # print(f"One candle: {client.get_candles(symbol='ETHUSDT', interval='1m', limit=1)[0]}")

    # bollinger_bands_strategy_example(close_prices)


if __name__ == '__main__':
    main()

