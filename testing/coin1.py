# -*- coding: utf-8 -*-
from math import ceil, floor
from random import randint, choice, uniform
from pdb import Pdb
 



class Crypto:

    def __init__(self, name, invest, buys, prices):
      self.name = name
      self.invest = invest
      self.buys = buys
      self.prices = prices

    def __str__(self):
      return self.name



class Stock:

    def __init__(self, name=None):
      if name:self.name = name

    def maxchange(self, cprice):
      fall = cprice / self.anual[1] * 100
      return fall

    def __str__(self):
      return self.name



price = Stock()
buy = Stock()
sell = Stock()
order = Stock

amd = Stock("AMD")
amd.anual = 27.41, 94.16
amd.lprice = 82.05
amd.lprice = 79.14

amzn = Stock("amazon")
amzn.anual = 1624.57, 3543.99
amzn.lprice = 3280.89
amzn.lprice = 3182.51

aapl = Stock("apple")
aapl.anual = 51.78, 137.58
aapl.lprice = 117.49
aapl.llprice = 113.85

fb = Stock("facebook")
fb.anual = 137.05, 304.35
fb.lprice = 274.39
fb.lprice = 268.55

ger30 = Stock("ger30")
ger30.anual = 7969.40, 13816.70
ger30.lprice = 13188.85

gold = Stock("gold")
gold.anual = 1445.45, 2074.74
gold.lprice = 1950.15
gold.lprice = 1948.37

goog = Stock("google")
goog.anual = 1012.09, 1731.31
goog.lprice = 1559.50
goog.lprice = 1534.59

intc = Stock("intel")
intc.anual = 43.59, 69.20
intc.lprice = 49.69
intc.lprice = 49.09
intc.lprice = 49.27

msft = Stock("microsoft")
msft.anual = 132.40, 232.63
msft.lprice = 211.61
msft.lprice = 206.11

nflx = Stock("netflix")
nflx.anual = 252.02, 574.48
nflx.lprice = 502.36
nflx.lprice = 481.59

nio = Stock("nio")
nio.anual = 1.19, 20.95
nio.lprice = 18.13
nio.lprice = 17.77

nsdq100 = Stock("nasdaq 100")
nsdq100.anual = 6627.85, 12466.10
nsdq100.lprice = 11352.35
nsdq100.lprice = 11265.00
nsdq100.lprice = 11246.49

nvda = Stock("nvidia")
nvda.anual = [166.5900, 588.2701]
nvda.buy = 490
nvda.sell = 529
nvda.lprice = 510.5892
nvda.lprice = 493.6739
nvda.lprice = 511.19

oil = Stock("oil")
oil.anual = 7.23, 65.42
oil.lprice = 37.81
oil.lprice = 37.65

tsla = Stock("tesla")
tsla.anual = 43.64, 501.65
tsla.lopen = 354.95
tsla.lclose = 408.4
tsla.lprice = 368.41
tsla.lprice = 372.55
tsla.lprice = 408.4

twtr = Stock("twiter")
twtr.anual = 19.98, 44.06
twtr.lprice = 39.66
twtr.lprice = 39.05

buy.msft = 222.78
buy.nvda = 489.8601
buy.aapl = 129.96
buy.goog = 1638.06
buy.nio = 19.28
buy.twtr = 40.68

sell.aapl = 137.43
sell.amzn = 3544.88
sell.goog = 1673.09
sell.nio = 19
sell.nvda = 509.8701
sell.msft = 215.14
sell.tsla = 445.26
sell.twtr = 40.36

lst = [amd, aapl, amzn, fb, gold, goog, intc, msft, nflx, nio, nsdq100,
      nvda, oil, tsla, twtr]



def fallindex(lst, srt=1):
  if srt: lst.sort(key=lambda x: x.maxchange(x.lprice), reverse=True)
  elif srt == 0: lst.sort(key=lambda x: x.maxchange(x.lprice))
  # for it in lst:
    # print(f"call� al {it.maxchange(it.lprice)}%.")



def gains(item, details=0):
  gn = 0
  item.valance = []
  for i in item.buys:
    value = round(item.prices[-1] / i * 100 - 100, 2)
    invest = item.invest[item.buys.index(i)]
    item.valance += [value * invest / 100]
    gn += value
    if details: print(f"valor {i}: {value}.")
  item.total_valance = round(sum(item.valance), 2)
  # item.valance = round(gn*sum(item.invest)/100,2)
  print(f"{item} {round(gn,2)}%.")
  print(f"valance {item.total_valance}.")



# Criptos.
ada = Crypto(name="ada",
            invest=[20, 20],
            buys=[1.3, 1.1],
            prices=[1.23, 1.2, 1.26, 1.31, 1.29, 1.25]
            )

bnb = Crypto(name="bnb",
        invest=[20, 20],
        buys=[244, 220],
        prices=[215, 211, 216, 219.5, 226.2, 229.1, 258, 248.2]
            )

dot = Crypto(name="dot",
       invest=[20],
       buys=[34],
       prices=[31.53, 30.9, 30.5, 32.3, 37.8]
            )

criptos = [ada, bnb, dot]
total_invest = 0
total_valance = 0
for i in criptos:
  gains(i, 0) 
  total_invest += sum(i.invest)
  total_valance += sum(i.valance) 
print(f"total invest {total_invest}.")
print(f"total valance {total_valance*100/total_invest}.")

Pdb().set_trace()
