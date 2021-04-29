import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

token_path = os.environ.get("TOKEN_PATH")
api_key = os.environ.get("API_KEY")
redirect_uri = os.environ.get("REDIRECT_URI")
account_id = os.environ.get("ACCOUNT_ID")

import tda
import json
import asyncio

# Auth and fetch AAPL

# try:
#     c = tda.auth.client_from_token_file(token_path, api_key)
# except FileNotFoundError:
#     from selenium import webdriver
#     with webdriver.Chrome() as driver:
#         c = tda.auth.client_from_login_flow(
#             driver, api_key, redirect_uri, token_path)

# r = c.get_price_history('AAPL',
#         period_type=tda.client.Client.PriceHistory.PeriodType.YEAR,
#         period=tda.client.Client.PriceHistory.Period.TWENTY_YEARS,
#         frequency_type=tda.client.Client.PriceHistory.FrequencyType.DAILY,
#         frequency=tda.client.Client.PriceHistory.Frequency.DAILY)
# assert r.status_code == 200, r.raise_for_status()
# print(json.dumps(r.json(), indent=4))


# Stream
client = tda.auth.easy_client(
  api_key=api_key,
  redirect_uri=redirect_uri,
  token_path=token_path
)

stream_client = tda.streaming.StreamClient(client, account_id=account_id)

async def quote(symbol):
    symbol = symbol.upper()
    res = client.get_quote(symbol)
    data = res.json()[symbol]
    print('Symbol: ' + data['symbol'])
    print('Open: $' + "{:.2f}".format(data['openPrice']))
    print('Close/Current: $' + "{:.2f}".format(data['regularMarketLastPrice']))
    modifier = "+" if data['netPercentChangeInDouble'] > 0 else "-"
    print('Percent Change: ' + modifier + "{:.2f}".format(round(data['netPercentChangeInDouble'], 2)) + "%")

async def login():
    await stream_client.login()
    await stream_client.quality_of_service(tda.streaming.StreamClient.QOSLevel.EXPRESS)

async def read_book_stream():
    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    stream_client.add_nasdaq_book_handler(
            lambda msg: print(json.dumps(msg, indent=4)))
    await stream_client.nasdaq_book_subs(['GOOG'])

    while True:
        await stream_client.handle_message()

# asyncio.run(read_book_stream())

# symbol = ""
# while symbol != "exit":
#     symbol = input("enter a symbol [exit to exit]: ")
#     asyncio.run(quote(symbol))


async def ohlcv_stream(symbols):
    symbols = [str.upper() for str in symbols]
    await login()
    print("Logged in!")
    stream_client.add_chart_equity_handler(lambda msg: print(json.dumps(msg, indent=4)))
    print ("Added Handler")
    await stream_client.chart_equity_subs(symbols)
    print("Handling Message")
    await stream_client.handle_message()

asyncio.run(ohlcv_stream(['gme']))
