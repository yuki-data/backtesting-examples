import backtradr as bt


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
        self.go_long()

    def recommend_buy(self):
        return True

    def action_buy(self):
        self.log('BUY CREATE, %.2f' % self.dataclose[0])
        # self.order = self.buy(exectype=bt.Order.Market, coc=False)
        # self.order = self.buy(exectype=bt.Order.Close)
        self.order = self.buy(coo=False, coc=True, exectype=bt.Order.Market)

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

class CustomBuyAndHold(BuyAndHold):
    def next(self):
        results["cash"].append(self.broker.get_cash())
        results["portfolio"].append(self.broker.getvalue())
        results["date"].append(self.datas[0].datetime.datetime(0))
        super().next()

    def next_open(self):
        if self.order:
            return
        # if not self.position:
        #     if self.recommend_buy() is True:
        #         self.log('BUY CREATE, %.2f' % self.data0.lines.open[0])
        #         self.order = self.buy(coo=True, coc=False)