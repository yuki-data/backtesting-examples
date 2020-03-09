import backtrader as bt


def run_bt(data, Strategy, Analyzer=None, analyzer_name="myanalyzer",
           trade_size=1, initial_cash=100000, commission_pct_rate=0.1,
           cheat_on_open=True, cheat_on_close=True, strategy_kwargs={},
           builtin_analyzers=None, builtin_observers=None, stdstats=True):
    """backtraderのバックテストを実行する。

    cerebro.run()および前処理(データ、ストラテジー、アナライザー、オブザーバーの追加)を実行する

    Args:
        Strategy (bt.Strategy): 自作のストラテジー
        Analyzer (bt.Analyzer): 自作のAnalyzer
        analyzer_name (str): 自作のAnalyzerの名前
        trade_size (int): 取引単位. 100なら100株単位で注文を出す
        initial_cash (int): 初期資金。少ないと注文がrejectされる。
        commission_pct_rate (float): 手数料率(%). 0.1なら売買代金の0.1%が手数料
        cheat_on_close (bool): cheat_on_closeを使う
        cheat_on_open (bool): cheat_on_openを使う
        strategy_kwargs (dict): 自作ストラテジーにわたすparams。{"gapup_threshold": 1}のように使う
        builtin_analyzers (List[bt.Analyzer]): backtraderの組み込みanalyzerで使うもの
        builtin_observers (List[bt.Observer]): backtraderの組み込みobserberで使うもの
        stdstats (bool): bt.Cerebroのデフォルトのobserverを有効にする

    Returns:
        bt.Cerebro: バックテスト実行後にプロットする場合、cerebro = run_bt()としてからcerebro.plot()とする

    Examples:
        # 引数の例
        builtin_analyzers=[
            bt.analyzers.DrawDown, bt.analyzers.Transactions, bt.analyzers.TradeAnalyzer],
        builtin_observers=[
            bt.observers.DrawDown,
            bt.observers.Trades, # ここの取引での損益
            bt.observers.BuySell,  # buy-sellボイントでのマーカー
            bt.observers.Value,  # 資産曲線
            ]
    """
    cerebro = bt.Cerebro(stdstats=stdstats, cheat_on_open=cheat_on_open)
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
    if builtin_observers:
        for observer in builtin_observers:
            cerebro.addobserver(observer)

    # Run over everything
    thestrats = cerebro.run()
    setattr(cerebro, "thestrats", thestrats)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()
    return cerebro
