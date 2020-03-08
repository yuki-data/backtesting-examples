import backtrader as bt


def run_bt(data, Strategy, Analyzer=None, analyzer_name="myanalyzer",
           trade_size=1, initial_cash=100000, commission_pct_rate=0.1,
           cheat_on_open=True, cheat_on_close=True, strategy_kwargs={},
           builtin_analyzers=None):
    cerebro = bt.Cerebro(stdstats=False, cheat_on_open=cheat_on_open)
    cerebro.addsizer(bt.sizers.SizerFix, stake=trade_size)

    if cheat_on_close:
        cerebro.broker.set_coc(True)
    cerebro.addstrategy(Strategy, **strategy_kwargs)
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    if Analyzer:
        cerebro.addanalyzer(Analyzer, _name=analyzer_name)
    if builtin_analyzers:
        for analyzer in builtin_analyzers:
            cerebro.addanalyzer(analyzer)

    # Set our desired cash start
    cerebro.broker.setcash(initial_cash)
    # 手数料
    cerebro.broker.setcommission(commission=commission_pct_rate * 0.01)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # オブザーバーのセット
    cerebro.addobserver(bt.observers.DrawDown)
    # cerebro.addobserver(bt.observers.Trades) # ここの取引での損益
    cerebro.addobserver(bt.observers.BuySell)  # buy-sellボイントでのマーカー
    cerebro.addobserver(bt.observers.Value)  # 資産曲線
    # Run over everything
    thestrats = cerebro.run()
    setattr(cerebro, "thestrats", thestrats)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()
    return cerebro
