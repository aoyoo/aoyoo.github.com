import json
import subprocess
import sys
import time

def get_cny_rate(line):
    #2020-09-27 USD CNY 6.82281678
    offset = line.find("2020") 
    d = line[offset:10]

    offset = line.find("USD CNY") 
    if offset == -1:
        print("find USD CNY fail")
        sys.exit(1)
    rate = float(line[offset + 8:])

    return (d, rate)

def get_upro_rate(line):
    #UPRO allocation ratio: 37.73% (anualized volatility: 271.19%, performance: -70.38%)
    ss = "UPRO allocation ratio: "
    offset = line.find(ss)
    if offset == -1:
        print("find " + ss + " fail")
        sys.exit(1)
    rate = float(line[offset + len(ss): len(ss) + 5])
    return rate

date_r = []
cny_r  = []
upro_r = []

r = open('txt', 'r')
for line in r.readlines():
    s = ''
    if "USD CNY" in line:
        date, rate = get_cny_rate(line)
        s += "date:{} CNY:{} ".format(date,rate)
        date_r.append(date)
        cny_r.append(rate)
    elif "Portfolio" in line:
        #print("Portfolio")
        pass
    elif "UPRO" in line:
        rate = get_upro_rate(line)
        s += "UPRO:{}".format(rate)
        upro_r.append(rate)
    elif "TMF" in line:
        #print("TMF")
        pass
    else:
        print("WHAT??")

    print (s)

if len(date_r) != len(cny_r) or len(date_r) != len(upro_r):
  print("error len")
  sys.exit(1)

#print (date_r)
print (cny_r)
print (upro_r)

