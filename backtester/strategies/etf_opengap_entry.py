import backtrader as bt
from ..indicators.percent_opengap import Opengap


class ETFOpengapStrategy(bt.Strategy):
    params = (("gapup_threshold", 1), ("unrealized_profit_threshold", 1))

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(dt, txt)

    def __init__(self):
        self.order = None
        self.dataclose = self.data0.lines.close
        self.dataopen = self.data0.lines.open
        self.buy_signal = Opengap(gapup_threshold=self.params.gapup_threshold).lines.open_gap_up

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log('order submit, %.2f' % order.created.price)
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            elif order.issell():
                profit_rate = (order.executed.price / self.price_buy - 1) * 100
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, profit rate %.3f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          profit_rate))

            self.after_order_completed(order)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        """
        sellのみ実行する。(sell or close)
        current barでのcloseが含み益の基準を満たすならcheat_on_closeで決済する
        """
        self.log(len(self))
        template = "{message}, {price:.2f}"

        if self.order:
            return
        if self.position:
            if self.recommend_sell() is True:
                self.log(template.format(message="SELL CREATE", price=self.dataclose[0]))
                self.order = self.sell(exectype=bt.Order.Market, coc=True, coo=False)

    def next_open(self):
        """
        opengapを基準に仕掛けるのでbuyはnext_openでのみ実行。
        sellは、含み益が基準なのでnext_openとnextの両方で判定する。
        buy, sellどちらもcheat_on_openとする
        """
        self.log("next_open {}".format(len(self)))
        template = "{message}(next_open), {price:.2f}"

        if self.order:
            return
        if not self.position:
            if self.recommend_buy():
                self.log(template.format(message="BUY CREATE", price=self.dataopen[0]))
                self.order = self.buy(exectype=bt.Order.Market, coc=False, coo=True)
        else:
            if self.recommend_sell() is True:
                self.log(template.format(message="SELL CREATE", price=self.dataopen[0]))
                self.order = self.sell(exectype=bt.Order.Market, coc=False, coo=True)

    def recommend_buy(self):
        opengap = (self.dataopen[0] - self.dataclose[-1]) / self.dataclose[-1] * 100
        if opengap > self.p.gapup_threshold:
            return True

    def execute_buy(self):
        self.log('BUY CREATE, %.2f' % self.dataclose[0])
        # self.order = self.buy(exectype=bt.Order.Market, coc=False)
        # self.order = self.buy(exectype=bt.Order.Close)
        self.order = self.buy(exectype=bt.Order.Market, coc=True, coo=False)
        # self.order = self.buy(coo=False, coc=True, exectype=bt.Order.Market)

    def recommend_sell(self):
        unrealized_profit = (self.dataopen[0] - self.price_buy) / self.price_buy * 100
        # return len(self) >= (self.bar_executed + 2)
        if unrealized_profit > self.p.unrealized_profit_threshold:
            return True

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
        if order.isbuy():
            self.price_buy = order.executed.price
