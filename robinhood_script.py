from __future__ import division
import time as timer
from Robinhood import Robinhood
from beautifultable import BeautifulTable
from config import USERNAME, PASSWORD
from datetime import datetime, time
import requests
import logging

def getSymbol(self, url):
    data = self.trader.get_url
    symbol = data['symbol']
    return symbol

url = 'https://min-api.cryptocompare.com/data/price?'
xrp_payload = {'fsym':'XRP', 'tsyms':'USD'}
btc_payload = {'fsym':'BTC', 'tsyms':'USD'}
eth_payload = {'fsym':'ETH', 'tsyms':'USD'}
ltc_payload = {'fsym':'LTC', 'tsyms':'USD'}

trader = Robinhood()
trader.login(username=USERNAME, password=PASSWORD)
watchlist_symbols = ['XXII', 'SWCH', 'MU', 'BABA', 'NVDA', 'AMZN', 'GOOGL',
                    'PYPL', 'BLFS', 'AMD', 'AAPL', 'NFLX', 'TSLA', 'AMAT',
                    'INTC', 'FB', 'MRVL', 'RYTM']
try:
    while True:
        xrp_response = requests.get(url, params=xrp_payload)
        btc_response = requests.get(url, params=btc_payload)
        eth_response = requests.get(url, params=eth_payload)
        ltc_response = requests.get(url, params=ltc_payload)
        xrp_response.raise_for_status()
        btc_response.raise_for_status()
        eth_response.raise_for_status()
        ltc_response.raise_for_status()
        xrp_json = xrp_response.json()
        btc_json = btc_response.json()
        eth_json = eth_response.json()
        ltc_json = ltc_response.json()
        xrp_price = xrp_json['USD']
        btc_price = btc_json['USD']
        eth_price = eth_json['USD']
        ltc_price = ltc_json['USD']

        portfolio = trader.portfolios()
        print ('Equity Value:', portfolio['equity'])
        account_details = trader.get_account()
        if 'margin_balances' in account_details:
            print ('Buying Power:', account_details['margin_balances']['unallocated_margin_cash'])

        positions = trader.securities_owned()
        symbols = []
        for position in positions['results']:
            data = trader.get_url(position['instrument'])
            symbols.append(data['symbol'])

        #Gets the prices for tickers owned in Robinhood
        ticker_data = trader.quotes_data(symbols) #json object containing data for each ticker owned
        prices = []
        previous_day_prices = []
        for quote in ticker_data:
            prices.append(quote['last_trade_price'])
            previous_day_prices.append(quote['previous_close'])

        #Gets the prices for tickers in watchlist
        watch_ticker_data = trader.quotes_data(watchlist_symbols)
        watch_prices = []
        watch_previous_day_prices = []
        for quote in watch_ticker_data:
            watch_prices.append(quote['last_trade_price'])
            watch_previous_day_prices.append(quote['previous_close'])

        #Gets the extended hours prices for tickers owned in Robinhood
        extended_hours_prices = []
        curr_time = datetime.now()
        if curr_time.time() >= time(16,00) or curr_time.time() < time(9,30):
            for quote in ticker_data:
                extended_hours_prices.append(quote['last_extended_hours_trade_price'])

        #Gets the extended hours prices for tickers in watchlist
        watch_extended_hours_prices = []
        watch_curr_time = datetime.now()
        if watch_curr_time.time() >= time(16,00) or watch_curr_time.time() < time(9,30):
            for quote in watch_ticker_data:
                watch_extended_hours_prices.append(quote['last_extended_hours_trade_price'])

        percent_changes = []
        i = 0
        for prev_price in previous_day_prices:
            current = float(prices[i])
            previous = float(prev_price)
            sub = current - previous
            decimal_change = sub/previous
            percent_change = decimal_change * 100
            percent_changes.append(percent_change)
            i+=1

        watch_percent_changes = []
        i = 0
        for prev_price in watch_previous_day_prices:
            current = float(watch_prices[i])
            previous = float(prev_price)
            sub = current - previous
            decimal_change = sub/previous
            percent_change = decimal_change * 100
            watch_percent_changes.append(percent_change)
            i+=1


        table = BeautifulTable()
        table.left_border_char = '|'
        table.right_border_char = '|'
        table.top_border_char = '_'
        table.bottom_border_char = '_'
        table.header_seperator_char = '_'
        table.row_seperator_char = '_'
        table.intersection_char = '$'
        table.column_seperator_char = '|'
        table.column_headers = ["Symbol", "Curr Price", "Quantity", "Equity", "Change", "Ext Hours"]
        i = 0
        for position in positions['results']:
            quantity = int(float(position['quantity']))
            symbol = symbols[i]
            price = prices[i]
            equity = float(price) * quantity
            change = percent_changes[i]
            if curr_time.time() >= time(16,00) or curr_time.time() <= time(9,30):
                ext_hours_price = extended_hours_prices[i]
                table.append_row([symbol, price, quantity, equity, change, ext_hours_price])
            else:
                ext_hours_price = price
                table.append_row([symbol, price, quantity, equity, change, ext_hours_price])
            i+=1

        table.sort("Equity")
        print(table)

        print("\nWatchlist")
        table = BeautifulTable()
        table.left_border_char = '|'
        table.right_border_char = '|'
        table.top_border_char = '_'
        table.bottom_border_char = '_'
        table.header_seperator_char = '_'
        table.row_seperator_char = '_'
        table.intersection_char = '$'
        table.column_seperator_char = '|'
        table.column_headers = ["Symbol", "Curr Price", "Change", "Ext Hours"]
        i = 0
        for index in watchlist_symbols:
            symbol = index
            price = watch_prices[i]
            change = watch_percent_changes[i]
            if curr_time.time() >= time(16,00) or curr_time.time() <= time(9,30):
                ext_hours_price = watch_extended_hours_prices[i]
                table.append_row([symbol, price, change, ext_hours_price])
            else:
                ext_hours_price = price
                table.append_row([symbol, price, change, ext_hours_price])
            i+=1

        table.sort("Change")
        print(table)

        print("\nCrypto Watchlist")
        table = BeautifulTable()
        table.left_border_char = '|'
        table.right_border_char = '|'
        table.top_border_char = '_'
        table.bottom_border_char = '_'
        table.header_seperator_char = '_'
        table.row_seperator_char = '_'
        table.intersection_char = '$'
        table.column_seperator_char = '|'
        table.column_headers = ["Symbol", "Curr Price"]
        table.append_row(['XRP', xrp_price])
        table.append_row(['BTC', btc_price])
        table.append_row(['ETH', eth_price])
        table.append_row(['LTC', ltc_price])
        print(table)
        timer.sleep(300)

except Exception as e:
    logging.exception("message")
