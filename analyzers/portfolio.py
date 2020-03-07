import backtrader as bt


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
