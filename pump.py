"""
for automating the buying/selling in a pump, use with caution.
"""
import datetime
import time
import math
import json
# import requests
import sys
# import decimal
from pprint import pprint
from binance.client import Client
from binance.enums import *

# Logical steps:
# Enter Coin
# Get price 
# Determine amount to buy/sell based on Price
# - Buy = Last price * .10
# - Sell = Last Price * .6
# - Round Down (BTC Amount / Price) = shares to purchase
# Create buy
# Create sell

# Get coin from command line argument
coin = str(sys.argv[1]).upper() + 'BTC'
# coin = 'ICNBTC'
print("Coin %s" % (coin))

# Get API Creds
creds = json.load(open('BinanceTradingCreds.json'))
api_key = creds["API_Key"]
api_secret = creds["API_Secret"]

# Create client object
client = Client(api_key, api_secret)

# Get symbol/coin info to determine tickSize
symbol_info = client.get_symbol_info(coin)
for f in symbol_info["filters"]:
    if f.get('tickSize'):
        tickSize = float(f.get('tickSize'))
        print("tickSize = {:.8f}".format(tickSize))

# klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1MINUTE, "1 minute ago PDT")
serverTime = client.get_server_time()["serverTime"]
print("Server Time: %s" % (datetime.datetime.fromtimestamp(serverTime/1000).strftime('%Y-%m-%d %H:%M:%S')))
print("Local Time:  %s" % (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
serverTime = serverTime-(2 * 60 * 1000)  # minutes * seconds * ms
print("Klines Time: %s" % (datetime.datetime.fromtimestamp(serverTime/1000).strftime('%Y-%m-%d %H:%M:%S')))
klines = client.get_klines(symbol=coin, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1, startTime=serverTime)
print("")

while not klines:
    print('klines response empty. Retrying....')
    klines = client.get_klines(symbol=coin, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1, startTime=serverTime)

close_time = klines[0][0]
close_price = float(klines[0][4])
print("Close Time: %s" % (datetime.datetime.fromtimestamp(close_time/1000).strftime('%Y-%m-%d %H:%M:%S')))
print("Close Price:   %s" % ("{:.8f}".format(close_price)))

# Current price for all tickers
prices = client.get_all_tickers()
current_price = float(next((price for price in prices if price["symbol"] == coin))['price'])
print("Current Price:   %s" % ("{:.8f}".format(current_price)))
# filter(lambda price: price['symbol'] == coin, prices)
# next((price for price in prices if price["symbol"] == coin))['price']
print("")

"""
prices = client.get_all_tickers()
for price in prices:
    print(price)
    if coin is price["symbol"]:
        print("found coin")
        current_price = price["price"]
        print("Current price: %s" % (current_price))
"""

balance = .25
print("Wallet Amount: %s" % (balance))
buy_price_perc = 1.1
price_to_buy = (int((close_price * buy_price_perc) / tickSize) * tickSize)
shares = math.floor(balance/price_to_buy)
print("Price to Buy:  {:.8f}".format(price_to_buy))
print("Shares to Buy:  %i" % (shares))
print("")

sell_price_perc = 1.6
price_to_sell = (int((close_price * sell_price_perc) / tickSize) * tickSize)
print("Price to Sell:  {:.8f}".format(price_to_sell))
print("Shares to Sell:  %i" % (shares))

"""
# order = client.create_test_order(
#     symbol=coin,
#     side=SIDE_BUY,
#     type=ORDER_TYPE_LIMIT,
#     timeInForce=TIME_IN_FORCE_GTC,
#     quantity=shares,
#     price=price_to_buy)
# print(order)
#
# order = client.create_test_order(
#     symbol=coin,
#     side=SIDE_SELL,
#     type=ORDER_TYPE_LIMIT,
#     timeInForce=TIME_IN_FORCE_GTC,
#     quantity=shares,
#     price=price_to_sell)
# print(order)

# order = client.order_limit_buy(symbol=coin,quantity=1000,price='0.00000750')
"""

buy = client.order_limit_buy(
    symbol=coin,
    timeInForce=TIME_IN_FORCE_GTC,
    newClientOrderId='autobuy'+coin,
    quantity=shares,
    price="{:.8f}".format(price_to_buy))
pprint(buy)

# status = buy["status"]
status = ""

# for counter in range(0,10):
while status != 'FILLED':
    order_status = client.get_order(
        symbol=coin,
        origClientOrderId='autobuy'+coin)
    status = order_status["status"]
    print("%s clientOrderId: %s  Status: %s" % (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), order_status["clientOrderId"], status))
    if status == 'FILLED':
        sale = client.order_limit_sell(
            symbol=coin,
            timeInForce=TIME_IN_FORCE_GTC,
            newClientOrderId='autosell'+coin,
            quantity=shares,
            price="{:.8f}".format(price_to_sell))
        pprint(sale)
        break
    time.sleep(.125)

"""
trades = client.get_recent_trades(symbol=coin)
price = float(0)
counter = int(0)
for trade in trades:
    price += float(trade["price"])
    #print('trade: %s price: %s' % (trade["price"], "{:.8f}".format(price)))
    counter += 1

avg_price = float("{:.8f}".format(price/counter))
print('Avg price: %s' % ("{:.8f}".format(avg_price)))
"""
