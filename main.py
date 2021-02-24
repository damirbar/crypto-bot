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
    to_crypto = 'SNX'
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
#[{'name': 'BNBUP', 'profit': 140.55699290562154}, {'name': 'UNIUP', 'profit': 140.0109463333918}, {'name': 'MATIC', 'profit': 137.8815713422672}, {'name': 'ETHUP', 'profit': 134.18319335641}, {'name': 'BLZ', 'profit': 131.3601650090164}, {'name': 'ADAUP', 'profit': 128.39033215229296}, {'name': 'EOSUP', 'profit': 124.78584296325802}, {'name': 'KEY', 'profit': 123.98361805458305}, {'name': 'MBL', 'profit': 123.0517523014053}, {'name': 'YFIUP', 'profit': 122.64103926863683}, {'name': 'FUN', 'profit': 121.19435344327631}, {'name': 'HARD', 'profit': 120.92480207233844}, {'name': 'ASR', 'profit': 120.87627737654627}, {'name': 'LTCUP', 'profit': 120.86733188433747}, {'name': 'AAVEUP', 'profit': 120.83808476872366}, {'name': 'SUSHIUP', 'profit': 120.59431269867457}, {'name': 'LINKUP', 'profit': 120.55459299051485}, {'name': 'XTZUP', 'profit': 120.48445864311145}, {'name': 'CTSI', 'profit': 120.48283533048068}, {'name': 'BZRX', 'profit': 120.2853681149478}, {'name': 'GTO', 'profit': 119.82197084933095}, {'name': 'MFT', 'profit': 119.455084975742}, {'name': 'KAVA', 'profit': 119.02004895456047}, {'name': 'PERL', 'profit': 118.55961568116314}, {'name': 'SNX', 'profit': 118.47202640380343}, {'name': 'UTK', 'profit': 118.33006134188894}, {'name': 'YFII', 'profit': 118.32953695937239}, {'name': 'ONT', 'profit': 118.26346189554845}, {'name': 'TCT', 'profit': 118.23960904585851}, {'name': 'ALGO', 'profit': 117.92706879971621}, {'name': 'TRXUP', 'profit': 117.65812674329005}, {'name': 'XLMUP', 'profit': 117.64267911589043}, {'name': 'SXP', 'profit': 117.61728113782485}, {'name': 'XMR', 'profit': 117.38577218372029}, {'name': 'WIN', 'profit': 117.29439963823698}, {'name': 'DENT', 'profit': 117.09616955123629}, {'name': 'BNB', 'profit': 117.08586340833533}, {'name': 'CAKE', 'profit': 116.6102407882413}, {'name': 'NEO', 'profit': 116.49671330311229}, {'name': 'SKL', 'profit': 116.47271853454838}, {'name': 'COTI', 'profit': 116.44735859200584}, {'name': 'AKRO', 'profit': 116.03035792760771}, {'name': 'WTC', 'profit': 115.84520076073171}, {'name': 'FLM', 'profit': 115.73552693910284}, {'name': 'VET', 'profit': 115.59118552043142}, {'name': 'CTK', 'profit': 115.3866937658365}, {'name': 'FTM', 'profit': 115.29497579323855}, {'name': 'STMX', 'profit': 115.26730051855212}, {'name': 'OCEAN', 'profit': 115.25836072509476}, {'name': 'YFI', 'profit': 114.65360618003912}, {'name': 'KNC', 'profit': 114.64432829257031}, {'name': 'LINK', 'profit': 114.63909663852249}, {'name': 'DGB', 'profit': 114.62386340939577}, {'name': 'AION', 'profit': 114.60719080878583}, {'name': 'ARPA', 'profit': 114.59873856596845}, {'name': 'BTT', 'profit': 114.53038282192321}, {'name': 'REN', 'profit': 114.4964630618428}, {'name': 'DATA', 'profit': 114.3323472644117}, {'name': 'COCOS', 'profit': 114.32610650260968}, {'name': 'DUSK', 'profit': 114.31828963687344}, {'name': 'ALPHA', 'profit': 114.25853235167607}, {'name': 'CVC', 'profit': 114.1569353641662}, {'name': 'QTUM', 'profit': 114.1369802428426}, {'name': 'TFUEL', 'profit': 113.82417283044913}, {'name': 'SAND', 'profit': 113.7223574412065}, {'name': 'XVS', 'profit': 113.71307065147106}, {'name': 'UNI', 'profit': 113.37873155065984}, {'name': 'RSR', 'profit': 113.36159966516769}, {'name': 'ICX', 'profit': 113.01825859569324}, {'name': 'TRB', 'profit': 113.00134071530151}, {'name': 'ONE', 'profit': 112.97419465924098}, {'name': 'WAVES', 'profit': 112.96237580926918}, {'name': 'BAL', 'profit': 112.87857447544413}, {'name': 'OGN', 'profit': 112.7795171968399}, {'name': 'ETC', 'profit': 112.73236718795916}, {'name': 'NANO', 'profit': 112.7301626818371}, {'name': 'SUSHI', 'profit': 112.70733738229444}, {'name': 'FILUP', 'profit': 112.61824974497792}, {'name': 'LTO', 'profit': 112.56489984391537}, {'name': 'TROY', 'profit': 112.38334291973445}, {'name': 'CTXC', 'profit': 112.31405071938133}, {'name': 'BCH', 'profit': 112.21234866083475}, {'name': 'DIA', 'profit': 112.12173053693924}, {'name': 'OG', 'profit': 112.07013063825562}, {'name': 'STORJ', 'profit': 112.03880910036803}, {'name': 'ONG', 'profit': 111.96375526043605}, {'name': 'GRT', 'profit': 111.94631247872907}, {'name': 'BTS', 'profit': 111.75403292438659}, {'name': 'ADA', 'profit': 111.61206440949564}, {'name': 'RUNE', 'profit': 111.60661064708253}, {'name': 'XEM', 'profit': 111.4935698699178}, {'name': 'ENJ', 'profit': 111.47984318670107}, {'name': 'LTC', 'profit': 111.30971376510718}, {'name': 'CRV', 'profit': 111.30338441547303}, {'name': 'IRIS', 'profit': 111.27008448222666}, {'name': 'HOT', 'profit': 111.25008352098759}, {'name': 'THETA', 'profit': 111.24857596418843}, {'name': 'PNT', 'profit': 110.947753211237}, {'name': 'ORN', 'profit': 110.91657580943556}, {'name': 'COMP', 'profit': 110.78387748558556}, {'name': 'DASH', 'profit': 110.77552911534033}, {'name': 'RLC', 'profit': 110.43817384663896}, {'name': 'BAT', 'profit': 110.38575316933688}, {'name': 'HBAR', 'profit': 110.24579994329856}, {'name': 'NPXS', 'profit': 110.09577981606519}, {'name': 'NBS', 'profit': 110.05114031905175}, {'name': 'VTHO', 'profit': 109.97546225944363}, {'name': 'REP', 'profit': 109.94550634555462}, {'name': 'WING', 'profit': 109.91433246370752}, {'name': 'JST', 'profit': 109.69154164634519}, {'name': 'DREP', 'profit': 109.68246638175523}, {'name': 'FET', 'profit': 109.64616137379562}, {'name': 'IOST', 'profit': 109.6333132588845}, {'name': 'ETH', 'profit': 109.60471634556697}, {'name': 'CELO', 'profit': 109.60433151946295}, {'name': 'AAVE', 'profit': 109.59847848625972}, {'name': 'MTL', 'profit': 109.5128737234302}, {'name': 'DNT', 'profit': 109.4292328776792}, {'name': 'RIF', 'profit': 109.4170857363689}, {'name': 'ATOM', 'profit': 109.41148409668793}, {'name': 'WAN', 'profit': 109.34425023190573}, {'name': 'SXPUP', 'profit': 109.29473979937713}, {'name': 'ZRX', 'profit': 109.27759938177252}, {'name': 'SFP', 'profit': 109.1125074138659}, {'name': 'EOS', 'profit': 109.0167028756534}, {'name': 'MKR', 'profit': 109.00680279968608}, {'name': 'COS', 'profit': 108.982734411767}, {'name': 'STPT', 'profit': 108.94944403471942}, {'name': 'AXS', 'profit': 108.90882545363672}, {'name': 'RVN', 'profit': 108.88419639080782}, {'name': '1INCH', 'profit': 108.88016850667483}, {'name': 'ZIL', 'profit': 108.74282978107702}, {'name': 'LIT', 'profit': 108.56339837261983}, {'name': 'BAND', 'profit': 108.54858434156229}, {'name': 'INJ', 'profit': 108.50383808625688}, {'name': 'LSK', 'profit': 108.45951105601242}, {'name': 'FIO', 'profit': 108.3541771366973}, {'name': 'AVAX', 'profit': 108.30322797210926}, {'name': 'BTCST', 'profit': 108.23728341773115}, {'name': 'TWT', 'profit': 108.19786781465585}, {'name': 'MANA', 'profit': 108.05362201184279}, {'name': 'XTZ', 'profit': 108.04422248975288}, {'name': 'BEAM', 'profit': 108.01188605946703}, {'name': 'WRX', 'profit': 107.88855422770504}, {'name': 'XLM', 'profit': 107.77085348029216}, {'name': 'BCHUP', 'profit': 107.74520258799187}, {'name': 'KMD', 'profit': 107.65263449483754}, {'name': 'PSG', 'profit': 107.5439870420823}, {'name': 'CHR', 'profit': 107.38089938769343}, {'name': 'UMA', 'profit': 107.35869474146033}, {'name': 'ROSE', 'profit': 107.32390408266014}, {'name': 'IOTA', 'profit': 107.29528724376421}, {'name': 'OMG', 'profit': 107.2781327728534}, {'name': 'BNT', 'profit': 107.16165972187022}, {'name': 'AUDIO', 'profit': 107.10471122804755}, {'name': 'IOTX', 'profit': 107.09530569693817}, {'name': 'BTCUP', 'profit': 107.07101801826425}, {'name': 'NULS', 'profit': 106.8887715727676}, {'name': 'MITH', 'profit': 106.88163866648037}, {'name': 'SUN', 'profit': 106.79590954154475}, {'name': 'ZEC', 'profit': 106.78174830739549}, {'name': 'DOGE', 'profit': 106.66747410910105}, {'name': 'SRM', 'profit': 106.6561202941509}, {'name': 'ZEN', 'profit': 106.57205626361824}, {'name': 'NEAR', 'profit': 106.56434355828266}, {'name': 'ANKR', 'profit': 106.55335394420673}, {'name': 'CELR', 'profit': 106.42483890334192}, {'name': 'TOMO', 'profit': 106.40333433662119}, {'name': 'SC', 'profit': 106.37063615404927}, {'name': 'STRAX', 'profit': 106.33453757224368}, {'name': 'XRPUP', 'profit': 106.22896065500382}, {'name': 'LRC', 'profit': 106.16499189844694}, {'name': 'HNT', 'profit': 106.06812610008379}, {'name': 'DODO', 'profit': 105.98335416853689}, {'name': 'KSM', 'profit': 105.78511733253887}, {'name': 'SOL', 'profit': 105.7680909215459}, {'name': 'FIRO', 'profit': 105.74464866141345}, {'name': 'MDT', 'profit': 105.59628325891431}, {'name': 'BEL', 'profit': 105.47497535670998}, {'name': 'TRX', 'profit': 105.47492422466851}, {'name': 'OXT', 'profit': 105.45979537044852}, {'name': 'REEF', 'profit': 105.43437067483116}, {'name': 'LUNA', 'profit': 105.39568889380693}, {'name': 'AVA', 'profit': 105.33839487624667}, {'name': 'FIL', 'profit': 105.19826142773705}, {'name': 'DOCK', 'profit': 105.13805027223894}, {'name': 'CKB', 'profit': 105.00193939667912}, {'name': 'BTC', 'profit': 104.89588294460363}, {'name': 'ANT', 'profit': 104.8281012174978}, {'name': 'NKN', 'profit': 104.67503373794686}, {'name': 'DOTUP', 'profit': 104.57311134140326}, {'name': 'BEAR', 'profit': 104.48079210297614}, {'name': 'TRU', 'profit': 104.36273504529534}, {'name': 'DCR', 'profit': 104.31998392217132}, {'name': 'FTT', 'profit': 104.23754039294715}, {'name': 'EGLD', 'profit': 104.0367482882285}, {'name': 'XZC', 'profit': 103.99443933503795}, {'name': 'BCC', 'profit': 103.9406513784638}, {'name': 'STX', 'profit': 103.69700506974428}, {'name': 'CHZ', 'profit': 103.49378659610183}, {'name': 'WNXM', 'profit': 103.37884436021086}, {'name': 'XRPBULL', 'profit': 103.36890823345988}, {'name': 'GXS', 'profit': 103.31889203948201}, {'name': 'VITE', 'profit': 103.10875463901161}, {'name': 'EOSBEAR', 'profit': 103.09015815148007}, {'name': 'JUV', 'profit': 102.85925762822903}, {'name': 'VEN', 'profit': 102.74270868692335}, {'name': 'XRP', 'profit': 102.66363735798627}, {'name': 'FILDOWN', 'profit': 102.58183913151915}, {'name': 'HIVE', 'profit': 102.5761666223264}, {'name': 'ATM', 'profit': 102.55259822477333}, {'name': 'UNFI', 'profit': 102.5165222808979}, {'name': 'NMR', 'profit': 102.49847246247502}, {'name': 'MCO', 'profit': 102.40230678132485}, {'name': 'ERD', 'profit': 102.3851887294706}, {'name': 'PAXG', 'profit': 102.2659981742269}, {'name': 'ARDR', 'profit': 101.82353509145638}, {'name': 'DOT', 'profit': 101.56698539590707}, {'name': 'HC', 'profit': 101.10918223990265}, {'name': 'SUSD', 'profit': 101.10790074716027}, {'name': 'DAI', 'profit': 100.9377611916405}, {'name': 'XRPBEAR', 'profit': 100.71872025543013}, {'name': 'BKRW', 'profit': 100.63965891437535}, {'name': 'TUSD', 'profit': 100.59088699615164}, {'name': 'BULL', 'profit': 100.15526265863976}, {'name': 'BCHABC', 'profit': 100.1316755438159}, {'name': 'ETHBEAR', 'profit': 100.10200384173429}, {'name': 'GBP', 'profit': 100.09307527409536}, {'name': 'USDS', 'profit': 100.04014854963364}, {'name': 'BCHDOWN', 'profit': 100.02069979970004}]


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

