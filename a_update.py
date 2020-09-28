import json
import subprocess
import sys
import time

import requests

# Author: Zebing Lin (https://github.com/linzebing)

from datetime import datetime, date
import math
import numpy as np
import time
import sys
import requests


def get_volatility_and_performance(symbol):
    download_url = "https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb=a7pcO//zvcW".format(symbol, start_timestamp, end_timestamp)
    lines = requests.get(download_url, cookies={'B': 'chjes25epq9b6&b=3&s=18'}).text.strip().split('\n')
    assert lines[0].split(',')[0] == 'Date'
    assert lines[0].split(',')[4] == 'Close'
    prices = []
    for line in lines[1:]:
        prices.append(float(line.split(',')[4]))
    prices.reverse()
    volatilities_in_window = []

    for i in range(window_size):
        volatilities_in_window.append(math.log(prices[i] / prices[i+1]))

    most_recent_date = datetime.strptime(lines[-1].split(',')[0], date_format).date()
    assert (date.today() - most_recent_date).days <= 4, "today is {}, most recent trading day is {}".format(date.today(), most_recent_date)

    return np.std(volatilities_in_window, ddof = 1) * np.sqrt(num_trading_days_per_year), prices[0] / prices[window_size] - 1.0


if __name__ == '__main__':

  time_str = time.strftime("%Y-%m-%d", time.localtime())

  base = 'USD'
  symbols = 'CNY'
  response = requests.get("https://api.currencyscoop.com/v1/latest?api_key=db56620137b26bcc472006a30a63ae43&base={}&symbols={}".format(base, symbols)).json()
  #{"meta":{"code":200,"disclaimer":"Usage subject to terms: https:\/\/currencyscoop.com\/terms"},"response":{"date":"2020-03-06T09:44:58Z","base":"USD","rates":{"CNY":6.94776903}}}
  #print(response)
  code = response["meta"]["code"]
  if code != 200:
    print("return code:{}".format(code))
    sys.exit(1)
  CNY_rate = response["response"]["rates"][symbols]

  print("{} {} {} {}\r\n".format(time_str, base, symbols, CNY_rate))

  symbols = ['UPRO', 'TMF']
  num_trading_days_per_year = 252
  window_size = 20
  date_format = "%Y-%m-%d"
  end_timestamp = int(time.time())
  start_timestamp = int(end_timestamp - (1.4 * (window_size + 1) + 4) * 86400)
  volatilities = []
  performances = []
  sum_inverse_volatility = 0.0
  for symbol in symbols:
      volatility, performance = get_volatility_and_performance(symbol)
      sum_inverse_volatility += 1 / volatility
      volatilities.append(volatility)
      performances.append(performance)
  
  print ("Portfolio: {}, as of {} (window size is {} days)".format(str(symbols), date.today().strftime('%Y-%m-%d'), window_size))
  UPRO_rate = float(100 / (volatilities[0] * sum_inverse_volatility))
      
  p = subprocess.Popen("""sed -i "17s/\(.*\)\(.*data:\)\(.*\)]/\\1\\2\\3, '{}']/" index.html""".format(time_str), shell=True)
  p.wait()
  p = subprocess.Popen("""sed -i "24s/\(.*\)\(.*data:\)\(.*\)]/\\1\\2\\3, {:.2f}]/" index.html""".format(UPRO_rate), shell=True)
  p.wait()

  p = subprocess.Popen("""sed -i "17s/\(.*\)\(.*data:\)\(.*\)]/\\1\\2\\3, '{}']/" cny.html""".format(time_str), shell=True)
  p.wait()
  p = subprocess.Popen("""sed -i "24s/\(.*\)\(.*data:\)\(.*\)]/\\1\\2\\3, {}]/" cny.html""".format(CNY_rate), shell=True)
  p.wait()


  print ("END time:{} CNY_rate:{} UPRO_rate:{}".format(time_str, CNY_rate, UPRO_rate))
  p = subprocess.Popen("git commit -am log:{}; git push".format(time_str), shell=True)
  p.wait()

#index.html
  #sed "s/\(.*\)\(category.*data:\)\(.*\)']/\1\2\3', '999']/" txt
  #sed "17s/\(.*\)\(.*data:\)\(.*\)]/\1\2\3, 999]/" txt
  # 17, 24, 27

