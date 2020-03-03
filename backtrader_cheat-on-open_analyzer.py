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
buy and holdをcheat on openと組み合わせて使う。
これにより、2日目の朝に、buyの実行と購入が同時にできるのをログで確認できる。

また、bt.Analyzerを自作して、これにより、資産曲線のデータを取れる。
これで、resultsというグローバル変数にアクセスせずにデータを取れる。
比較するために両方で資産曲線をとっている。
"""


class MyAnalyzer(bt.Analyzer):
    """
    # Usage
    cerebro.addanalyzer(MyAnalyzer, _name='myanalyzer')
    strats = cerebro.run()
    strat = thestrats[0]
    print('Sharpe Ratio:', strat.analyzers.myanalyzer.get_analysis())
    """
    def start(self):
        self.results = {
            "cash": [],
            "portfolio": [],
            "date": []
        }

    def next(self):
        self.results["cash"].append(self.strategy.broker.get_cash())
        self.results["portfolio"].append(self.strategy.broker.getvalue())
        self.results["date"].append(self.datas[0].datetime.datetime(0))

    def get_analysis(self):
        return self.results


class BuyAndHold(bt.Strategy):
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
        # self.go_long()
        pass

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

    def go_long(self):
        if self.order:
            return
        if not self.position:
            if self.recommend_buy() is True:
                self.action_buy()
        else:
            if self.recommend_sell() is True:
                self.action_sell()


results = {}


class CustomBuyAndHold(BuyAndHold):
    """
    BuyAndHoldの資産曲線データをキープするためのクラス。
    ここではcheat on openを使っている。
    ログを見ると、buyの実行は2日目のopenで実行され、即座にopenで買えているのがわかる。
    cheat on openを有効にすると、ストラテジーにてnext_openを実行できる。
    next_openでは、openの直前にnextと実質同じことを実行する。
    """
    def start(self):
        results["cash"] = []
        results["portfolio"] = []
        results["date"] = []

    def next(self):
        """
        Analyzerでの資産曲線と比較するためにここでも資産曲線データをとる。
        本来nextでデータを取らなくていい。
        """
        results["cash"].append(self.broker.get_cash())
        results["portfolio"].append(self.broker.getvalue())
        results["date"].append(self.datas[0].datetime.datetime(0))
        super().next()

    def next_open(self):
        if self.order:
            return
        if not self.position:
            if self.recommend_buy() is True:
                self.log('BUY CREATE, %.2f' % self.data0.lines.open[0])
                self.order = self.buy(coo=True, coc=False)

"""
`cerebro.addanalyzer(Analyzer, _name=analyzer_name)`と
`thestrats = cerebro.run(); setattr(cerebro, "thestrats", thestrats)`
により、あとからanalyzerのデータを取れる
"""
def run_bt(data, Strategy, Analyzer=None, analyzer_name="myanalyzer"):
    cerebro = bt.Cerebro(stdstats=False, cheat_on_open=True)
    cerebro.addstrategy(Strategy)
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    if Analyzer:
        cerebro.addanalyzer(Analyzer, _name=analyzer_name)

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
    thestrats = cerebro.run()
    setattr(cerebro, "thestrats", thestrats)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()
    return cerebro


path = Path("SPDR_S&P500_ETF_2010-2020.csv")
df = pd.read_csv(path, parse_dates=["Date"])
data = bt.feeds.PandasData(dataname=df.set_index("Date"))
cerebro = run_bt(data, Strategy=CustomBuyAndHold)
s2 = pd.DataFrame(cerebro.thestrats[0].analyzers.myanalyzer.get_analysis())
s = pd.DataFrame(results)
"""
analyzerがうまく機能しているのでs == s2になる。
"""
assert (s == s2).all().all()
