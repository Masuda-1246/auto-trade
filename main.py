import configparser
import pandas as pd
import time
from coincheck import Coincheck
from utils.notify import send_message_to_line

conf = configparser.ConfigParser()
conf.read("config.ini")
ACCESS_KEY = conf["coincheck"]["access_key"]
SECRET_KEY = conf["coincheck"]["secret_key"]

cols = ['price']
df = pd.DataFrame(index=[], columns=cols)

coincheck = Coincheck(access_key=ACCESS_KEY, secret_key=SECRET_KEY)

interval = 60*10
duration = 20
amount = 0.005

send_message_to_line("自動トレードを開始します")
while True:
  position = coincheck.position
  time.sleep(interval)

  if not position.get('jpy'):
    send_message_to_line("日本円講座が０です")
    raise

  record = pd.Series(coincheck.last, index=df.columns)
  df.loc[len(df)] = record

  if len(df) < duration:
    continue

  df["SMA"] = df["price"].rolling(window=duration).mean()
  df["std"] = df["price"].rolling(window=duration).std()
  df["+2sigma"] = df["SMA"] + 2*df["std"]
  df["-2sigma"] = df["SMA"] - 2*df["std"]

  if 'btc' in position.keys():
    if df["+2sigma"].iloc[-1] < df["price"].iloc[-1] and coincheck.rate < df['price'].iloc[-1]:
      params = {
        'order_type': 'market_sell',
        'pair': 'btc_jpy',
        'market_buy_amount': position['btc']
      }
      r = coincheck.order(params)
      send_message_to_line(r)
      print("sell!!!")
  else:
    if df["price"].iloc[-1] < df["-2sigma"].iloc[-1]:
      market_buy_amount = coincheck.rate({
        'order_type': 'buy',
        'pair': 'btc_jpy',
        'amount': amount
      })
      params = {
        'order_type': 'market_buy',
        'pair': 'btc_jpy',
        'market_buy_amount': market_buy_amount['price']
      }
      r = coincheck.order(params)
      send_message_to_line(r)
      print("buy!!!")