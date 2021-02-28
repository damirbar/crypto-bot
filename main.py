#!/usr/bin/python3
from binance.exceptions import BinanceAPIException

import nexmo
from api_connection.api_client import ApiClient
from api_connection.api_secrets import NEXMO_API_KEY, NEXMO_API_SECRET, MY_PHONE_NUMBER
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


def send_sms(message_text):
    client = nexmo.Client(key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)

    client.send_message({
        'from': 'Nexmo',
        'to': MY_PHONE_NUMBER,
        'text': message_text,
    })


def trader_bot_run(money_to_play):
    from_coin = 'USDT'
    to_crypto = 'BNBUP'
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
    bot.notify_action_function(send_sms)

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
            close_prices = client.get_close_prices_dataframe(symbol=f'{coin_name}USDT', interval='1m', limit=590)
            res = bollinger_bands_example(close_prices, init_money=100, plot=False)
            if res > 100:
                coins_rating.append({'name': coin_name, 'profit': res})
        except BinanceAPIException as e:
            pass

    coins_rating = sorted(coins_rating, key=lambda x: x['profit'], reverse=True)
    print(coins_rating)
#[{'name': 'BLZ', 'profit': 123.12840152122217}, {'name': 'MATIC', 'profit': 115.11783170945074}, {'name': 'BNBUP', 'profit': 114.68620736330084}, {'name': 'FTM', 'profit': 114.6713183404487}, {'name': 'DNT', 'profit': 114.63396666094916}, {'name': 'ORN', 'profit': 114.38346917658254}, {'name': 'TCT', 'profit': 113.35657368608207}, {'name': 'DOTDOWN', 'profit': 112.94891749597485}, {'name': 'DUSK', 'profit': 112.66791627892235}, {'name': 'REEF', 'profit': 112.57503028345191}, {'name': 'TRXUP', 'profit': 112.52773683873869}, {'name': 'UNIUP', 'profit': 112.38215876942864}, {'name': 'DREP', 'profit': 112.1183311753053}, {'name': 'OG', 'profit': 112.03226958667896}, {'name': 'PERL', 'profit': 111.56305449636923}, {'name': 'BNB', 'profit': 111.53509280487802}, {'name': 'DIA', 'profit': 111.43480925823198}, {'name': 'DOTUP', 'profit': 111.09030845962043}, {'name': 'FILUP', 'profit': 110.92578159738643}, {'name': 'COS', 'profit': 110.81111044686217}, {'name': 'TROY', 'profit': 110.75504968107116}, {'name': 'WRX', 'profit': 110.47507550435431}, {'name': 'PNT', 'profit': 110.33553624217078}, {'name': 'CAKE', 'profit': 110.09450828268656}, {'name': 'GTO', 'profit': 110.06122072663696}, {'name': 'WTC', 'profit': 110.05229916290969}, {'name': 'COTI', 'profit': 109.95927657428076}, {'name': 'NBS', 'profit': 109.95560393377922}, {'name': 'NPXS', 'profit': 109.30095005532704}, {'name': 'IRIS', 'profit': 109.25634064077867}, {'name': 'KEY', 'profit': 109.21853292821665}, {'name': 'ETHUP', 'profit': 109.18735473674485}, {'name': 'CELO', 'profit': 109.1837875196865}, {'name': 'ALPHA', 'profit': 109.16622760906505}, {'name': 'BAL', 'profit': 109.13183409815997}, {'name': 'ICX', 'profit': 108.56596160499467}, {'name': 'ALGO', 'profit': 108.54268994218613}, {'name': 'EOSUP', 'profit': 108.07015143801314}, {'name': 'STORJ', 'profit': 108.04610145333311}, {'name': 'PSG', 'profit': 107.91655094972295}, {'name': 'NKN', 'profit': 107.89596948158099}, {'name': 'BCHUP', 'profit': 107.74520258799187}, {'name': 'COMP', 'profit': 107.59994448811798}, {'name': 'AAVEUP', 'profit': 107.52436887979994}, {'name': 'DODO', 'profit': 107.43607784562677}, {'name': 'FUN', 'profit': 107.32219395361162}, {'name': 'DATA', 'profit': 107.27499948655142}, {'name': 'LIT', 'profit': 107.2136023955628}, {'name': 'NEAR', 'profit': 107.09261474133157}, {'name': 'CTXC', 'profit': 107.05417033022087}, {'name': 'COCOS', 'profit': 106.97083444925386}, {'name': 'ADAUP', 'profit': 106.88803398125793}, {'name': 'LINKUP', 'profit': 106.81399985095597}, {'name': 'STMX', 'profit': 106.55651001424955}, {'name': 'BZRX', 'profit': 106.50274750437347}, {'name': 'AION', 'profit': 106.49618049147583}, {'name': 'BAND', 'profit': 106.41676233621625}, {'name': 'INJ', 'profit': 106.26095831807581}, {'name': 'UTK', 'profit': 106.19679673313544}, {'name': 'RVN', 'profit': 106.15437118822135}, {'name': 'FIO', 'profit': 106.02850946334249}, {'name': 'TRB', 'profit': 105.99693755757124}, {'name': 'AUDIO', 'profit': 105.90537214737627}, {'name': 'ETC', 'profit': 105.89445107341115}, {'name': 'TFUEL', 'profit': 105.84088346616848}, {'name': 'DCR', 'profit': 105.80051769882155}, {'name': 'WAN', 'profit': 105.79944144572829}, {'name': 'MFT', 'profit': 105.79045580889259}, {'name': 'AXS', 'profit': 105.77784671192879}, {'name': 'IOTA', 'profit': 105.77643500290583}, {'name': 'THETA', 'profit': 105.72242040833106}, {'name': 'ENJ', 'profit': 105.6707661719773}, {'name': 'HNT', 'profit': 105.55650072700786}, {'name': 'YFIUP', 'profit': 105.55095077694963}, {'name': 'JUV', 'profit': 105.51584083807211}, {'name': 'ATM', 'profit': 105.51327933958794}, {'name': 'BAT', 'profit': 105.48824943967624}, {'name': 'ARPA', 'profit': 105.45871114001592}, {'name': 'ATOM', 'profit': 105.45651657707775}, {'name': 'DOT', 'profit': 105.38889911336405}, {'name': 'BTCST', 'profit': 105.38878681666387}, {'name': 'XMR', 'profit': 105.29472501808067}, {'name': 'BCH', 'profit': 105.22994962462747}, {'name': 'WIN', 'profit': 105.16404568275986}, {'name': 'IOTX', 'profit': 105.16093585993579}, {'name': 'ANKR', 'profit': 105.15597387337631}, {'name': 'ASR', 'profit': 105.13049818793341}, {'name': 'RLC', 'profit': 105.02716550676448}, {'name': 'BTCUP', 'profit': 105.01330280957937}, {'name': 'VET', 'profit': 104.98948132861197}, {'name': 'DOCK', 'profit': 104.88747620482525}, {'name': 'CRV', 'profit': 104.88563457798035}, {'name': 'ONG', 'profit': 104.8629879123885}, {'name': 'KAVA', 'profit': 104.85868016717001}, {'name': 'MANA', 'profit': 104.85038165223324}, {'name': 'NULS', 'profit': 104.84765109669978}, {'name': 'HOT', 'profit': 104.84589161707513}, {'name': 'VITE', 'profit': 104.82640759645845}, {'name': 'ZIL', 'profit': 104.7717433691807}, {'name': 'HBAR', 'profit': 104.73103392338899}, {'name': 'LTCUP', 'profit': 104.64247800660588}, {'name': 'FTT', 'profit': 104.59336233629551}, {'name': 'ONE', 'profit': 104.53518175772092}, {'name': 'NEO', 'profit': 104.51496499783883}, {'name': 'XLMUP', 'profit': 104.50565092941218}, {'name': 'DGB', 'profit': 104.50084433955524}, {'name': 'BEAR', 'profit': 104.48079210297614}, {'name': 'QTUM', 'profit': 104.45071714658023}, {'name': 'OMG', 'profit': 104.4471020185432}, {'name': 'ONT', 'profit': 104.42724226784044}, {'name': 'FIRO', 'profit': 104.39758081287985}, {'name': 'AKRO', 'profit': 104.35031473277148}, {'name': 'MTL', 'profit': 104.34938150455358}, {'name': 'MITH', 'profit': 104.32566526625183}, {'name': 'YFII', 'profit': 104.19482469554013}, {'name': 'SNX', 'profit': 104.07074752481988}, {'name': 'XZC', 'profit': 103.99443933503795}, {'name': 'BCC', 'profit': 103.9406513784638}, {'name': 'YFI', 'profit': 103.91322459240122}, {'name': 'UNFI', 'profit': 103.86473540342887}, {'name': 'VTHO', 'profit': 103.8498173318346}, {'name': 'REN', 'profit': 103.80915507367313}, {'name': 'FLM', 'profit': 103.7649839409877}, {'name': 'OXT', 'profit': 103.66516608416347}, {'name': 'ETH', 'profit': 103.66386769269926}, {'name': 'XLM', 'profit': 103.65727179309978}, {'name': 'SUSHIUP', 'profit': 103.63142625460142}, {'name': 'MBL', 'profit': 103.547298604119}, {'name': 'LTO', 'profit': 103.51726450620089}, {'name': 'HARD', 'profit': 103.47681693861841}, {'name': 'CVC', 'profit': 103.45580662416528}, {'name': 'ANT', 'profit': 103.41130604048237}, {'name': 'CTK', 'profit': 103.37058272259677}, {'name': 'XRPBULL', 'profit': 103.36890823345988}, {'name': 'BNT', 'profit': 103.35522493465582}, {'name': 'RUNE', 'profit': 103.27092677576533}, {'name': 'RSR', 'profit': 103.25486638341832}, {'name': 'CELR', 'profit': 103.23533186105658}, {'name': 'EOSBEAR', 'profit': 103.09015815148007}, {'name': 'SXPUP', 'profit': 103.07742570667634}, {'name': 'TWT', 'profit': 103.0511422619635}, {'name': 'OGN', 'profit': 103.03369037880995}, {'name': 'SFP', 'profit': 103.01693508891789}, {'name': 'XRPUP', 'profit': 102.93155986964433}, {'name': 'VEN', 'profit': 102.74270868692335}, {'name': 'MDT', 'profit': 102.71176264467174}, {'name': 'NMR', 'profit': 102.70066145238704}, {'name': 'WAVES', 'profit': 102.67019029261233}, {'name': 'FILDOWN', 'profit': 102.66048906282948}, {'name': 'BTC', 'profit': 102.60278663298286}, {'name': 'STRAX', 'profit': 102.44822191246094}, {'name': 'MCO', 'profit': 102.40230678132485}, {'name': 'ERD', 'profit': 102.3851887294706}, {'name': 'CTSI', 'profit': 102.31232399078}, {'name': 'AVAX', 'profit': 102.25101540759765}, {'name': 'REP', 'profit': 102.24185971958366}, {'name': 'OCEAN', 'profit': 102.23443647009357}, {'name': 'TOMO', 'profit': 102.16385260174913}, {'name': 'UMA', 'profit': 102.13652932350807}, {'name': 'DENT', 'profit': 102.04710605468887}, {'name': 'FET', 'profit': 101.99585470678485}, {'name': 'LRC', 'profit': 101.96975101885016}, {'name': 'GXS', 'profit': 101.93126854026801}, {'name': 'KMD', 'profit': 101.85610955137147}, {'name': 'SC', 'profit': 101.82702535989743}, {'name': 'SKL', 'profit': 101.78947639551566}, {'name': 'SOL', 'profit': 101.75799443972846}, {'name': 'FIL', 'profit': 101.74546629586071}, {'name': 'IOST', 'profit': 101.7090214704103}, {'name': '1INCH', 'profit': 101.68435378698041}, {'name': 'ZEC', 'profit': 101.67284506436182}, {'name': 'SUSHI', 'profit': 101.65196977284369}, {'name': 'ADA', 'profit': 101.62596963673967}, {'name': 'DASH', 'profit': 101.60372240355831}, {'name': 'KSM', 'profit': 101.59333796127098}, {'name': 'LINK', 'profit': 101.57969472262111}, {'name': 'PAXG', 'profit': 101.42856180718063}, {'name': 'LUNA', 'profit': 101.27784432851685}, {'name': 'SXP', 'profit': 101.2687688963003}, {'name': 'XTZ', 'profit': 101.26394117370451}, {'name': 'DOGE', 'profit': 101.26005627686479}, {'name': 'EOS', 'profit': 101.18875259599473}, {'name': 'BTCDOWN', 'profit': 101.17593570553971}, {'name': 'BEAM', 'profit': 101.16474384944463}, {'name': 'AAVE', 'profit': 101.1578914380983}, {'name': 'HC', 'profit': 101.10918223990265}, {'name': 'LTC', 'profit': 101.03029155469042}, {'name': 'SUSD', 'profit': 101.00692282288655}, {'name': 'BTS', 'profit': 101.0011423049115}, {'name': 'DAI', 'profit': 100.9377611916405}, {'name': 'TRX', 'profit': 100.8835650799028}, {'name': 'TUSD', 'profit': 100.87283234721625}, {'name': 'XVS', 'profit': 100.83380919140409}, {'name': 'WING', 'profit': 100.78281592677007}, {'name': 'JST', 'profit': 100.76404685817083}, {'name': 'UNI', 'profit': 100.72764610379815}, {'name': 'XTZUP', 'profit': 100.71954065424153}, {'name': 'XRPBEAR', 'profit': 100.71872025543013}, {'name': 'BKRW', 'profit': 100.63965891437535}, {'name': 'RIF', 'profit': 100.59201930566755}, {'name': 'XEM', 'profit': 100.56251326021243}, {'name': 'NANO', 'profit': 100.50653995166023}, {'name': 'SRM', 'profit': 100.46471893980288}, {'name': 'SUSHIDOWN', 'profit': 100.4200134469296}, {'name': 'AUD', 'profit': 100.23707045283446}, {'name': 'HIVE', 'profit': 100.22148238336231}, {'name': 'BULL', 'profit': 100.15526265863976}, {'name': 'BCHABC', 'profit': 100.1316755438159}, {'name': 'SUN', 'profit': 100.1079038808213}, {'name': 'ETHBEAR', 'profit': 100.10200384173429}, {'name': 'USDC', 'profit': 100.09005604042484}, {'name': 'USDS', 'profit': 100.04014854963364}, {'name': 'BCHDOWN', 'profit': 100.02069979970004}, {'name': 'BUSD', 'profit': 100.00998700390005}, {'name': 'GBP', 'profit': 100.00724430818224}]


def process_binance_websocket_message(msg):
    """
    Message format:
    {
        "e": "kline",                                   # event type
        "E": 1499404907056,                             # event time
        "s": "ETHBTC",                                  # symbol
        "k": {
            "t": 1499404860000,                 # start time of this bar
            "T": 1499404919999,                 # end time of this bar
            "s": "ETHBTC",                      # symbol
            "i": "1m",                          # interval
            "f": 77462,                         # first trade id
            "L": 77465,                         # last trade id
            "o": "0.10278577",                  # open
            "c": "0.10278645",                  # close
            "h": "0.10278712",                  # high
            "l": "0.10278518",                  # low
            "v": "17.47929838",                 # volume
            "n": 4,                             # number of trades
            "x": false,                                 # whether this bar is final
            "q": "1.79662878",                  # quote volume
            "V": "2.34879839",                  # volume of active buy
            "Q": "0.24142166",                  # quote volume of active buy
            "B": "13279784.01349473"    # can be ignored
            }
    }
    """
    print(f"Message type: {msg['e']}")
    print(msg)


def get_continuous_kline():
    client = ApiClient()
    client.connect()

    from binance.websockets import BinanceSocketManager
    bm = BinanceSocketManager(client.get_raw_client())
    # start any sockets here, i.e a trade socket
    # conn_key = bm.start_trade_socket('ETHUSDT', process_binance_websocket_message)
    conn_key = bm.start_kline_socket('DOGEUSDT', process_binance_websocket_message, interval='1m')
    # then start the socket manager
    bm.start()


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

