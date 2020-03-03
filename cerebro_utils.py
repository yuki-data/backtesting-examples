"""
backtraderのプロットカスタマイズ支援ツール

update: 170425
create: 170425

backtraderのcerebro.run()した後で、

    cerebro.plot(style="candle", bardown='blue', iplot=False, voloverlay=True)

とすると、observerとdataの全てがプロットされる。
見やすくするために、run()の後で、プロットするものを変更したい。

- CerebroUtils.swicth_cerebro_data_plot: dataのプロットをオンオフ
- CerebroUtils.swicth_observer_plot: 指定したobserverのプロットをオンオフ
- CerebroUtils.show_observer_names: 使用したobserverのリストを表示
"""
import pandas as pd


class CerebroUtils():
    """cerebroのバックテスト結果の取得に便利なツール
    cerbro_bind_results()でcerebroとresultsをbindしていないと、他の関数は動作しない。
    """
    @staticmethod
    def cerbro_bind_results(cerebro, results):
        """cerebroのプロパティにresultsをセットする。
        Usage:
        results = cerebro.run()
        cerbro_bind_results(cerebro, results)
        """
        setattr(cerebro, "results", results)

    @staticmethod
    def swicth_observer_plot(cerebro, name_observer, strat_num=0):
        """cerebroのobserverのプロットのオンオフを切り替える

        - name_observer: str, "drawdown", "value"など
        """
        plotinfo = cerebro.results[strat_num].observers.getbyname(name_observer).plotinfo
        plotinfo.plot = not (plotinfo.plot)

    @staticmethod
    def show_observer_names(cerebro, strat_num=0):
        """observerをリスト表示"""
        return cerebro.results[strat_num].observers.getnames()

    @staticmethod
    def show_analyzer_names(cerebro, strat_num=0):
        """analyzerをリスト表示"""
        return cerebro.results[strat_num].analyzers.getnames()

    @staticmethod
    def swicth_cerebro_data_plot(cerebro, data_num=0):
        """cerebroのデータのプロットのオンオフを切り替える"""
        cerebro.datas[data_num].plotinfo.plot = not (cerebro.datas[data_num].plotinfo.plot)

    @staticmethod
    def report_transaction_df(cerebro, strat_num=0, fillna=True):
        """cerebroから取引の結果と資産曲線を取得してdfで返す

        Usage:
        cerebro.run()の前に、cerebro.addanalyzer(bt.analyzers.Transactions)で
        transactionをanalyzerとしてセットしておく。
        run()の後に、

            df = report_transaction_df(cerebro)

        で結果を取得。

        Explanations:
        cerebro.results[0].analyzers.transactions.get_analysis()でOrderedDictで結果を取得できる。
        dict_trade_results.values()がdatetime.datetimeで各トレードの日時
        dict_trade_results.keys()が[-100, 7464.0, 0, , -746400.0]のように、[size, price, 0, , cashflow]形式のリスト
        """
        dict_trade_results = cerebro.results[0].analyzers.transactions.get_analysis()
        df_trade_results = pd.DataFrame(list(dict_trade_results.values()), index=list(dict_trade_results.keys()), columns=["A"])
        df_trade_results = df_trade_results.assign(Buysell=df_trade_results.A.apply(lambda f: f[0]),
                                                   Price=df_trade_results.A.apply(lambda f: f[1]),
                                                   Cashflow=df_trade_results.A.apply(lambda f: f[4]))
        df_trade_results["Return"] = df_trade_results.Cashflow + df_trade_results.Cashflow.where(df_trade_results.Buysell == 100).shift(1)
        if fillna:
            df_trade_results.Return.fillna(0, inplace=True)
        df_trade_results["CumReturn"] = df_trade_results.Return.cumsum()
        del df_trade_results["A"]
        return df_trade_results
