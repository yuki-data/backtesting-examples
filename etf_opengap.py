"""
created 200304

open gapで1%上がったら買うstrategy。利益が1%出たら利確する。
"""

import backtrader as bt


class Opengap(bt.Indicator):
    params = (("gapup_threshold", 1),)
    lines = ("open_gap_up",)

    def __init__(self):
        pct_relative_open = bt.DivByZero(self.data0.lines.open - self.data0.lines.close(-1), self.data0.lines.close(-1), bt.NAN)
        self.lines.open_gap_up = (pct_relative_open * 100) > self.p.gapup_threshold


class ETFOpengapStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(dt, txt)

    def __init__(self):
        self.order = None
        self.dataclose = self.data0.lines.close
        self.dateopen = self.data0.lines.open
        self.buy_signal = Opengap(gapup_threshold=1).lines.open_gap_up

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log('order submit, %.2f' % order.created.price)
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.after_order_completed(order)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):
        self.log(len(self))
        # self.log('Close, %.2f' % self.dataclose[0])
        # self.log('self.buy_signal, %.2f' % self.buy_signal[0])
        self.go_long()

    def recommend_buy(self):
        if self.buy_signal == 1:
            return True

    def execute_buy(self):
        self.log('BUY CREATE, %.2f' % self.dataclose[0])
        # self.order = self.buy(exectype=bt.Order.Market, coc=False)
        # self.order = self.buy(exectype=bt.Order.Close)
        self.order = self.buy(exectype=bt.Order.Market, coc=False)
        # self.order = self.buy(coo=False, coc=True, exectype=bt.Order.Market)

    def recommend_sell(self):
        return len(self) >= (self.bar_executed + 2)

    def execute_sell(self):
        self.log('SELL CREATE, %.2f' % self.dataclose[0])
        self.order = self.sell(exectype=bt.Order.Market)

    def go_long(self):
        if self.order:
            return
        if not self.position:
            if self.recommend_buy() is True:
                self.execute_buy()
        else:
            if self.recommend_sell() is True:
                self.execute_sell()

    def after_order_completed(self, order):
        self.bar_executed = len(self)
