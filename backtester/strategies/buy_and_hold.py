import backtrader as bt


class BuyAndHold(bt.Strategy):
    """
    初日のnextでbuyの注文を出して翌日のopenで購入し、移行はholdするストラテジー
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
        self.go_long()

    def recommend_buy(self):
        return True

    def execute_buy(self):
        self.log('BUY CREATE, %.2f' % self.dataclose[0])
        self.order = self.buy(exectype=bt.Order.Market, coc=False, coo=False)

    def recommend_sell(self):
        return

    def execute_sell(self):
        self.log('SELL CREATE, %.2f' % self.dataclose[0])
        self.order = self.sell(exectype=bt.Order.Market, coc=False, coo=False)

    def go_long(self):
        if self.order:
            return
        if not self.position:
            if self.recommend_buy() is True:
                self.execute_buy()
        else:
            if self.recommend_sell() is True:
                self.execute_sell()
