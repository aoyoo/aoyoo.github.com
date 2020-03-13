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

  base = 'USD'
  symbols = 'CNY'

  response = requests.get("https://api.currencyscoop.com/v1/latest?api_key=db56620137b26bcc472006a30a63ae43&base={}&symbols={}".format(base, symbols)).json()
  #{"meta":{"code":200,"disclaimer":"Usage subject to terms: https:\/\/currencyscoop.com\/terms"},"response":{"date":"2020-03-06T09:44:58Z","base":"USD","rates":{"CNY":6.94776903}}}
  #print(response)
  code = response["meta"]["code"]
  if code != 200:
    print("return code:{}".format(code))
    sys.exit(1)
  rate = response["response"]["rates"][symbols]

  time_str = time.strftime("%Y-%m-%d", time.localtime())

  echo_str = "{} {} {} {}\r\n".format(time_str, base, symbols, rate)
  print(echo_str)

  if len(sys.argv) == 1:
      symbols = ['UPRO', 'TMF']
  else:
      symbols = sys.argv[1].split(',')
      for i in range(len(symbols)):
          symbols[i] = symbols[i].strip().upper()
  
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
  for i in range(len(symbols)):
      print ('{} allocation ratio: {:.2f}% (anualized volatility: {:.2f}%, performance: {:.2f}%)'.format(symbols[i], float(100 / (volatilities[i] * sum_inverse_volatility)), float(volatilities[i] * 100), float(performances[i] * 100)))
  



  with open('index.html', 'a') as w:
    w.write(echo_str)

  #subprocess.Popen("python3 inverse_volatility_caculation-master/inverse_volatility.py >> index.html")


  subprocess.Popen("git commit -am log:{}".format(time_str), shell=True)
  subprocess.Popen("git push", shell=True)


  #out_bytes = subprocess.check_output(['git','commit', '-am', 'log:{}'.format(time_str)])
  #print("git ci output:{}".format(out_bytes.decode('utf-8')))

  #out_bytes = subprocess.check_output(['git','push'])
  #print("git push output:{}".format(out_bytes.decode('utf-8')))


