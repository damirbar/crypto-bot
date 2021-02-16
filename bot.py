#!/usr/bin/python3

from api_connection.api_client import ApiClient


def main():
    
    client = ApiClient()
    client.connect()

    eth_balance = client.get_asset_balance(asset='ETH')
    print(eth_balance)

    balance = client.get_balance()

    for coin in balance:
        print(coin)

    r_client = client.get_raw_client()



if __name__ == '__main__':
    main()

