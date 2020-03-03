"""
pandasのみでbuy and holdストラテジーの資産曲線を作成する。

colaboratoryでbacktraderを使う場合には、
!pip install git+https://github.com/yuki-data/backtrader@dev/ito/remove-tkagg-import
としてtkaggを回避する。
"""
import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# %matplotlib inline
from pathlib import Path
import backtrader as bt


"""
pandasで資産曲線を作る場合には、二日目からエントリーする.
backtraderは、一日目からエントリーできないため。
"""
def make_portfolio(df, buy_signal):
    df = df.copy()
    df = buy_signal(df)
    df["Cost"] = df.Buy * df.Open

    df["Cum_Cost"] = df.Cost.cumsum()

    df["Position"] = df.Buy.cumsum().shift()

    df["Daily_Return"] = df.Open.diff() * df.Position

    df["Cum_Return"] = df.Daily_Return.cumsum()
    df["portfolio"] = df.Buy.cumsum() * df.Close - df.Cum_Cost
    return df


def buy_and_hold(df):
    """
    二日目のOpenで買う。以降はholdする。
    """
    df["Buy"] = 0
    df.at[1, "Buy"] = 1
    return df


path = Path("SPDR_S&P500_ETF_2010-2020.csv")
df = pd.read_csv(path, parse_dates=["Date"])
df_1 = make_portfolio(df, buy_and_hold)
df_1.set_index("Date").portfolio.plot()

"""
backtraderでbuy and holdの資産曲線を作成する。
"""


class BuyAndHold(bt.Strategy):
    """
    買うだけのストラテジー。sellで何もしない。ピラミッディングしない。
    そのため、buy and holdになる。
    一日目にbuyが実行され、実際に買われるのは、(cheat on openがないので)翌日のOpenになる。
    """
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(dt, txt)

    def __init__(self):
        self.order = None
        self.dataclose = self.data0.lines.close

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log('order submit, %.2f' % order.created.price)
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):
        # self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        if not self.position:
            if self.recommend_buy() is True:
                self.action_buy()
        else:
            if self.recommend_sell() is True:
                self.action_sell()

    def recommend_buy(self):
        return True

    def action_buy(self):
        self.log('BUY CREATE, %.2f' % self.dataclose[0])
        self.order = self.buy(exectype=bt.Order.Market)

    def recommend_sell(self):
        return

    def action_sell(self):
        self.log('SELL CREATE, %.2f' % self.dataclose[0])
        self.order = self.sell(exectype=bt.Order.Market)


results = {}


class CustomBuyAndHold(BuyAndHold):
    """
    BuyAndHoldの資産曲線データをキープするためのクラス。
    """
    def start(self):
        results["cash"] = []
        results["portfolio"] = []
        results["date"] = []

    def next(self):
        results["cash"].append(self.broker.get_cash())
        results["portfolio"].append(self.broker.getvalue())
        results["date"].append(self.datas[0].datetime.datetime(0))
        super().next()


def run_bt(data, Strategy):
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.addstrategy(Strategy)
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # オブザーバーのセット
    cerebro.addobserver(bt.observers.DrawDown)
    # cerebro.addobserver(bt.observers.Trades) # ここの取引での損益
    cerebro.addobserver(bt.observers.BuySell) # buy-sellボイントでのマーカー
    cerebro.addobserver(bt.observers.Value) # 資産曲線
    # Run over everything
    cerebro.run()
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()
    return cerebro

"""
これでbacktraderとpandasでのbuy and holdの結果が一致する。
"""

data = bt.feeds.PandasData(dataname=df.set_index("Date"))
cerebro = run_bt(data, Strategy=CustomBuyAndHold)
# cerebro.plot()
s = pd.DataFrame(results)
s.set_index("date").portfolio.plot()
