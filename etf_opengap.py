"""
created 200304

open gapで1%上がったら買うstrategy。利益が1%出たら利確する。

# バックテストの実行
data = bt.feeds.PandasData(dataname=df.set_index("Date"), fromdate=datetime.datetime(2011, 3, 1), todate=datetime.datetime(2011, 5, 1))
cerebro = run_bt(data, Strategy=ETFOpengapStrategy, Analyzer=MyAnalyzer, strategy_kwargs={"gapup_threshold": 1})

# analyzerの結果の確認
s = pd.DataFrame(cerebro.thestrats[0].analyzers.myanalyzer.get_analysis())
s.set_index("date").portfolio.plot() # 資産曲線プロット

"""

# import backtrader as bt


# class MyAnalyzer(bt.Analyzer):
#     """
#     # Usage
#     cerebro.addanalyzer(MyAnalyzer, _name='myanalyzer')
#     strats = cerebro.run()
#     strat = thestrats[0]
#     print('Sharpe Ratio:', strat.analyzers.myanalyzer.get_analysis())
#     """

#     def start(self):
#         self.results = {
#             "cash": [],
#             "portfolio": [],
#             "date": []
#         }

#     def next(self):
#         self.results["cash"].append(self.strategy.broker.get_cash())
#         self.results["portfolio"].append(self.strategy.broker.getvalue())
#         self.results["date"].append(self.datas[0].datetime.datetime(0))

#     def get_analysis(self):
#         return self.results


# class Opengap(bt.Indicator):
#     params = (("gapup_threshold", 1),)
#     lines = ("open_gap_up",)

#     def __init__(self):
#         pct_relative_open = bt.DivByZero(self.data0.lines.open - self.data0.lines.close(-1), self.data0.lines.close(-1), bt.NAN)
#         self.lines.open_gap_up = (pct_relative_open * 100) > self.p.gapup_threshold


# class ETFOpengapStrategy(bt.Strategy):
#     params = (("gapup_threshold", 1), ("unrealized_profit_threshold", 1))

#     def log(self, txt, dt=None):
#         dt = dt or self.datas[0].datetime.date(0)
#         print(dt, txt)

#     def __init__(self):
#         self.order = None
#         self.dataclose = self.data0.lines.close
#         self.dataopen = self.data0.lines.open
#         self.buy_signal = Opengap(gapup_threshold=self.params.gapup_threshold).lines.open_gap_up

#     def notify_order(self, order):
#         if order.status in [order.Submitted, order.Accepted]:
#             self.log('order submit, %.2f' % order.created.price)
#             return
#         if order.status in [order.Completed]:
#             if order.isbuy():
#                 self.log('BUY EXECUTED, %.2f' % order.executed.price)
#             elif order.issell():
#                 self.log('SELL EXECUTED, %.2f' % order.executed.price)
#             self.after_order_completed(order)
#         elif order.status in [order.Canceled, order.Margin, order.Rejected]:
#             self.log('Order Canceled/Margin/Rejected')
#         self.order = None

#     def next(self):
#         """
#         sellのみ実行する。(sell or close)
#         current barでのcloseが含み益の基準を満たすならcheat_on_closeで決済する
#         """
#         self.log(len(self))
#         template = "{message}, {price:.2f}"

#         if self.order:
#             return
#         if self.position:
#             if self.recommend_sell() is True:
#                 self.log(template.format(message="SELL CREATE", price=self.dataclose[0]))
#                 self.order = self.sell(exectype=bt.Order.Market, coc=True, coo=False)

#     def next_open(self):
#         """
#         opengapを基準に仕掛けるのでbuyはnext_openでのみ実行。
#         sellは、含み益が基準なのでnext_openとnextの両方で判定する。
#         buy, sellどちらもcheat_on_openとする
#         """
#         self.log("next_open {}".format(len(self)))
#         template = "{message}(next_open), {price:.2f}"

#         if self.order:
#             return
#         if not self.position:
#             if self.recommend_buy():
#                 self.log(template.format(message="BUY CREATE", price=self.dataopen[0]))
#                 self.order = self.buy(exectype=bt.Order.Market, coc=False, coo=True)
#         else:
#             if self.recommend_sell() is True:
#                 self.log(template.format(message="SELL CREATE", price=self.dataopen[0]))
#                 self.order = self.sell(exectype=bt.Order.Market, coc=False, coo=True)

#     def recommend_buy(self):
#         opengap = (self.dataopen[0] - self.dataclose[-1]) / self.dataclose[-1] * 100
#         if opengap > self.p.gapup_threshold:
#             return True

#     def execute_buy(self):
#         self.log('BUY CREATE, %.2f' % self.dataclose[0])
#         # self.order = self.buy(exectype=bt.Order.Market, coc=False)
#         # self.order = self.buy(exectype=bt.Order.Close)
#         self.order = self.buy(exectype=bt.Order.Market, coc=True, coo=False)
#         # self.order = self.buy(coo=False, coc=True, exectype=bt.Order.Market)

#     def recommend_sell(self):
#         unrealized_profit = (self.dataopen[0] - self.price_bought) / self.price_bought * 100
#         # return len(self) >= (self.bar_executed + 2)
#         if unrealized_profit > self.p.unrealized_profit_threshold:
#             return True

#     def execute_sell(self):
#         self.log('SELL CREATE, %.2f' % self.dataclose[0])
#         self.order = self.sell(exectype=bt.Order.Market)

#     def go_long(self):
#         if self.order:
#             return
#         if not self.position:
#             if self.recommend_buy() is True:
#                 self.execute_buy()
#         else:
#             if self.recommend_sell() is True:
#                 self.execute_sell()

#     def after_order_completed(self, order):
#         self.bar_executed = len(self)
#         if order.isbuy():
#             self.price_bought = order.executed.price


# def run_bt(data, Strategy, Analyzer=None, analyzer_name="myanalyzer", cheat_on_open=True, cheat_on_close=True, strategy_kwargs={}):
#     cerebro = bt.Cerebro(stdstats=False, cheat_on_open=cheat_on_open)
#     if cheat_on_close:
#         cerebro.broker.set_coc(True)
#     cerebro.addstrategy(Strategy, **strategy_kwargs)
#     # Add the Data Feed to Cerebro
#     cerebro.adddata(data)

#     if Analyzer:
#         cerebro.addanalyzer(Analyzer, _name=analyzer_name)

#     # Set our desired cash start
#     cerebro.broker.setcash(100000.0)
#     # Print out the starting conditions
#     print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
#     # オブザーバーのセット
#     cerebro.addobserver(bt.observers.DrawDown)
#     # cerebro.addobserver(bt.observers.Trades) # ここの取引での損益
#     cerebro.addobserver(bt.observers.BuySell)  # buy-sellボイントでのマーカー
#     cerebro.addobserver(bt.observers.Value)  # 資産曲線
#     # Run over everything
#     thestrats = cerebro.run()
#     setattr(cerebro, "thestrats", thestrats)

#     # Print out the final result
#     print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
#     # cerebro.plot()
#     return cerebro
