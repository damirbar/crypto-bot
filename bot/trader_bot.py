import time


class TraderBot:

    def __init__(self):
        self._dataframe = None
        self.indicators = []
        self._money_to_play = 0

        self._update_dataframe_function = None
        self._update_dataframe_args     = None

        self._check_balance_function = None

        self._market_buy_function  = None
        self._market_sell_function = None

        self._check_price_function = None

        self._notify_action_function = None

        self._from_coin = None
        self._to_crypto = None
        self.trading_symbol = None

    @property
    def from_coin(self):
        return self._from_coin

    @from_coin.setter
    def from_coin(self, coin):
        self._from_coin = coin
        self.trading_symbol = f'{self._to_crypto}{self._from_coin}'

    @property
    def to_crypto(self):
        return self._to_crypto

    @to_crypto.setter
    def to_crypto(self, coin):
        self._to_crypto = coin
        self.trading_symbol = f'{self._to_crypto}{self._from_coin}'

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, df):
        self._dataframe = df

    def add_indicator(self, strategy):
        self.indicators.append(strategy)

    def initialize_indicators(self):
        for indicator in self.indicators:
            indicator.dataframe = self._dataframe
            indicator.initialize_indicator()

    def get_expediences(self):
        expediences = {}
        for indicator in self.indicators:
            expediences[indicator.__class__.__name__] = indicator.action_expedience()
        return expediences

    @property
    def money_to_play(self):
        return self._money_to_play

    @money_to_play.setter
    def money_to_play(self, money):
        self._money_to_play = money

    def update_dataframe(self):
        self._dataframe = self._update_dataframe_function(
            symbol=self._update_dataframe_args['symbol'],
            interval=self._update_dataframe_args['interval']
        )
        self.initialize_indicators()
        # print(f"Updated the dataframe: {self._dataframe}")

    def get_balance(self, asset):
        return float(self._check_balance_function(asset)['free'])

    def update_dataframe_function(self, func, args):
        print("Setting the update-dataframe function")
        self._update_dataframe_function = func
        self._update_dataframe_args = args

    def check_balance_function(self, func):
        print("Setting the check-balance function")
        self._check_balance_function = func

    def buy_function(self, func):
        print("Setting the buy function")
        self._market_buy_function = func

    def sell_function(self, func):
        print("Setting the sell function")
        self._market_sell_function = func

    def check_price_function(self, func):
        print("Setting the check-price function")
        self._check_price_function = func

    def notify_action_function(self, func):
        print("Setting the notify function")
        self._notify_action_function = func

    def act_and_loop(self):

        iteration = 0
        while True:
            self.update_dataframe()
            log_str = f"iteration {iteration}"
            coin_balance   = self.get_balance(self._from_coin)
            crypto_balance = self.get_balance(self._to_crypto)
            log_str += f" {self._from_coin} balance: {coin_balance}"
            log_str += f" {self._to_crypto} balance: {crypto_balance}"

            crypto_worth = self._check_price_function(self.trading_symbol)

            bb_exp = self.get_expediences()['BollingerBands']

            log_str += f" expedience: {bb_exp}"
            print(log_str)

            if bb_exp['buy'] > 0.9 and coin_balance >= 10:
                if crypto_worth < 1:
                    amount_to_buy = int(coin_balance/crypto_worth)
                else:
                    amount_to_buy = round(coin_balance/crypto_worth, 3)
                print(f"Attempt to buy {amount_to_buy} {self.trading_symbol}")
                self._notify_action_function(f"Buying {self._to_crypto} at price {crypto_worth}")
                self._market_buy_function(self.trading_symbol, amount_to_buy)

            elif bb_exp['sell'] > 0.9 and crypto_balance * crypto_worth >= 10:
                print(f"Attempt to buy {crypto_balance} {self.trading_symbol}")
                self._notify_action_function(f"Selling {self._to_crypto} at price {crypto_worth}")
                self._market_sell_function(self.trading_symbol, round(crypto_balance, 3))

            time.sleep(10)
            iteration += 1

        pass
