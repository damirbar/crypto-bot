#!/usr/bin/python3
from binance.exceptions import BinanceAPIException

from api_connection.api_client import ApiClient
from bot.trader_bot import TraderBot
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


def trader_bot_run(money_to_play):
    from_coin = 'USDT'
    to_crypto = 'XEM'
    trading_symbol = f'{to_crypto}{from_coin}'

    # Initialize the API client
    client = ApiClient()
    client.connect()

    # Initialize the bot
    bot = TraderBot()
    bot.from_coin = from_coin
    bot.to_crypto = to_crypto
    bot.add_indicator(BollingerBands())
    bot.money_to_play = money_to_play

    # Provide functionality
    bot.buy_function(client.market_buy)
    bot.sell_function(client.market_sell)
    bot.check_price_function(client.get_current_price)
    bot.update_dataframe_function(client.get_close_prices_dataframe, {'symbol': trading_symbol, 'interval': '1m'})
    bot.check_balance_function(client.get_asset_balance)

    bot.act_and_loop()


def bollinger_bands_strategy_example(dataframe):
    bb = BollingerBands(dataframe)
    bb.std_spacing = 1.96
    bb.initialize_indicator()
    bb_dataframe = bb.dataframe.dropna()
    print(bb_dataframe)

    return bb.action_expedience()


def bollinger_bands_example(close_prices, init_money=100, plot=True):
    bb = BollingerBands(close_prices)
    bb.std_spacing = 1.96
    bb.initialize_indicator()
    bb_dataframe = bb.dataframe.dropna()
    # print(bb_dataframe)

    bought = False

    money = init_money
    crypto_amount = 0
    for i, entry in bb_dataframe.iterrows():
        if entry['Close'] < entry['Lower Band']:
            if not bought:
                # print(f"Start buying from price {entry['Close']}")
                bought = True
            if money > 0:
                crypto_amount = money / entry['Close']
                money = 0
                # print(f"Buy at index {i}, price {entry['Close']}, Lower Band {entry['Lower Band']}")
        if entry['Close'] > entry['Upper Band']:
            if crypto_amount > 0:
                money = entry['Close'] * crypto_amount
                crypto_amount = 0
                # print(f"Sell at index {i}, price {entry['Close']}, Upper Band {entry['Upper Band']}")
        i += 1

    if money > 0:
        print(f"Started with {init_money} and finished with {money}")
        result = money
    else:
        print(f"Started with {init_money} and finished with {crypto_amount * bb_dataframe['Close'].iloc[-1]}")
        result = crypto_amount * bb_dataframe['Close'].iloc[-1]

    if plot:
        visualize(bb_dataframe)

    return result


def find_best_coin():
    client = ApiClient()
    client.connect()
    coins = client.get_raw_client().get_account()['balances']
    coins_rating = []
    for coin in coins:
        try:
            coin_name = coin['asset']
            print(f"Checking for {coin_name}")
            close_prices = client.get_close_prices_dataframe(symbol=f'{coin_name}USDT', interval='1m')
            res = bollinger_bands_example(close_prices, init_money=100, plot=False)
            if res > 100:
                coins_rating.append({'name': coin_name, 'profit': res})
        except BinanceAPIException as e:
            pass

    print(coins_rating)
# Result: [{'name': 'NEO', 'profit': 100.31936648652702}, {'name': 'BNB', 'profit': 102.65033353252441}, {'name': 'BNT', 'profit': 104.56050117372573}, {'name': 'BCC', 'profit': 102.84975166527369}, {'name': 'DNT', 'profit': 107.13750001073159}, {'name': 'MCO', 'profit': 103.7911943733003}, {'name': 'ZRX', 'profit': 100.55406780277032}, {'name': 'WTC', 'profit': 101.78390030190675}, {'name': 'FUN', 'profit': 100.92053820931014}, {'name': 'KNC', 'profit': 101.07682991898928}, {'name': 'REP', 'profit': 100.75944286136547}, {'name': 'ENJ', 'profit': 100.84135003401589}, {'name': 'VEN', 'profit': 102.37951987963459}, {'name': 'KMD', 'profit': 106.56202631039757}, {'name': 'BTS', 'profit': 101.16738509982919}, {'name': 'XZC', 'profit': 102.30012192670497}, {'name': 'XLM', 'profit': 101.60617745566405}, {'name': 'GTO', 'profit': 101.75621042836565}, {'name': 'AION', 'profit': 104.00229219296672}, {'name': 'IOST', 'profit': 109.68072016925318}, {'name': 'XEM', 'profit': 109.92483818589649}, {'name': 'WAN', 'profit': 101.46863919806465}, {'name': 'TUSD', 'profit': 100.3207324321515}, {'name': 'ZEN', 'profit': 100.74096424173746}, {'name': 'NPXS', 'profit': 105.75765486866047}, {'name': 'MFT', 'profit': 102.95243446192377}, {'name': 'DENT', 'profit': 100.39846291359305}, {'name': 'DOCK', 'profit': 103.82054437094833}, {'name': 'ONG', 'profit': 100.06765348545065}, {'name': 'PAX', 'profit': 100.12014917720474}, {'name': 'DCR', 'profit': 101.51954370467558}, {'name': 'USDC', 'profit': 100.1201401525593}, {'name': 'MITH', 'profit': 100.70270168517307}, {'name': 'BCHABC', 'profit': 100.1316755438159}, {'name': 'REN', 'profit': 100.92718324775872}, {'name': 'BTT', 'profit': 108.10853327391946}, {'name': 'USDS', 'profit': 100.04014854963364}, {'name': 'FET', 'profit': 101.34189557895927}, {'name': 'TFUEL', 'profit': 103.79597133184716}, {'name': 'MATIC', 'profit': 103.15890073092045}, {'name': 'ATOM', 'profit': 102.56116235510638}, {'name': 'ONE', 'profit': 101.97259026161319}, {'name': 'FTM', 'profit': 104.79096648097223}, {'name': 'CHZ', 'profit': 101.21705316052086}, {'name': 'COS', 'profit': 104.01532558747823}, {'name': 'ERD', 'profit': 102.93157930971817}, {'name': 'PERL', 'profit': 100.08077211399026}, {'name': 'TOMO', 'profit': 100.82097030384124}, {'name': 'BUSD', 'profit': 100.18029142919576}, {'name': 'BAND', 'profit': 102.0815428917317}, {'name': 'GBP', 'profit': 100.33825063955629}, {'name': 'KAVA', 'profit': 100.20076044486596}, {'name': 'VITE', 'profit': 104.94202518942804}, {'name': 'OGN', 'profit': 106.87079885052273}, {'name': 'BEAR', 'profit': 104.19790187165039}, {'name': 'ETHBEAR', 'profit': 100.43346743061419}, {'name': 'XRPBULL', 'profit': 102.30931805794606}, {'name': 'XRPBEAR', 'profit': 102.20709124697379}, {'name': 'EOSBEAR', 'profit': 103.5599216084067}, {'name': 'LTO', 'profit': 102.89464441440286}, {'name': 'MBL', 'profit': 102.53540118766908}, {'name': 'BKRW', 'profit': 100.31907345094326}, {'name': 'CHR', 'profit': 101.25427934246837}, {'name': 'BTCDOWN', 'profit': 108.96922235868881}, {'name': 'FIO', 'profit': 100.95451112946832}, {'name': 'STMX', 'profit': 100.21472438685223}, {'name': 'COMP', 'profit': 101.90728073515885}, {'name': 'SXP', 'profit': 108.80856442413719}, {'name': 'SNX', 'profit': 101.58262555319367}, {'name': 'DAI', 'profit': 100.81874836035274}, {'name': 'ETHDOWN', 'profit': 103.79963789195808}, {'name': 'ADADOWN', 'profit': 105.4661848218895}, {'name': 'LINKDOWN', 'profit': 100.06930259702364}, {'name': 'BNBUP', 'profit': 103.73027564743954}, {'name': 'BNBDOWN', 'profit': 112.36751067960584}, {'name': 'XTZDOWN', 'profit': 104.71308163795288}, {'name': 'AVA', 'profit': 102.1389773064706}, {'name': 'ANT', 'profit': 102.8660747219127}, {'name': 'NMR', 'profit': 100.0736875061186}, {'name': 'RSR', 'profit': 101.07299993658005}, {'name': 'PAXG', 'profit': 101.27715126340016}, {'name': 'KSM', 'profit': 107.06630252970744}, {'name': 'DIA', 'profit': 101.35608048193173}, {'name': 'EOSDOWN', 'profit': 102.87424719117978}, {'name': 'TRXDOWN', 'profit': 106.65457163686455}, {'name': 'DOTUP', 'profit': 100.52266146952955}, {'name': 'DOTDOWN', 'profit': 111.91750911953159}, {'name': 'NBS', 'profit': 100.98172903205932}, {'name': 'LTCDOWN', 'profit': 104.4903892696125}, {'name': 'SUN', 'profit': 102.73431149077877}, {'name': 'CAKE', 'profit': 101.99671015913324}, {'name': 'ALPHA', 'profit': 104.8899451103215}, {'name': 'UTK', 'profit': 100.83682776847515}, {'name': 'NEAR', 'profit': 102.97512793070449}, {'name': 'AAVE', 'profit': 100.49504577007724}, {'name': 'SXPUP', 'profit': 117.77205182565312}, {'name': 'SXPDOWN', 'profit': 161.3671875}, {'name': 'YFIDOWN', 'profit': 101.25178318478991}, {'name': 'AUDIO', 'profit': 103.5937213281401}, {'name': 'BCHUP', 'profit': 110.57405163724606}, {'name': 'BCHDOWN', 'profit': 101.8148544859606}, {'name': 'ROSE', 'profit': 105.26282005059214}, {'name': 'AAVEUP', 'profit': 102.83420878749025}, {'name': 'AAVEDOWN', 'profit': 107.71766581094919}, {'name': 'SUSD', 'profit': 100.3887889962643}, {'name': 'SUSHIDOWN', 'profit': 108.2436669123687}, {'name': 'XLMUP', 'profit': 100.028452968719}, {'name': 'CELO', 'profit': 100.33429211369389}, {'name': 'TWT', 'profit': 103.06502283961515}, {'name': '1INCH', 'profit': 101.57447520965292}, {'name': 'RIF', 'profit': 101.6161956777831}, {'name': 'LIT', 'profit': 100.27536182945532}, {'name': 'SFP', 'profit': 102.29459567462912}, {'name': 'DODO', 'profit': 103.93941755853909}]


def main2():
    find_best_coin()


def main():
    client = ApiClient()
    client.connect()

    print(trader_bot_run(40))


def main3():
    
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

    close_prices = client.get_close_prices_dataframe(symbol='LINKUSDT', interval='1m')
    print(close_prices)

    bollinger_bands_example(close_prices, init_money=100, plot=False)

    # print(f"One candle: {client.get_candles(symbol='ETHUSDT', interval='1m', limit=1)[0]}")


if __name__ == '__main__':
    main()

