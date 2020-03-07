import datetime
from pathlib import Path
import pandas as pd
import backtrader as bt
# from etf_opengap import run_bt, ETFOpengapStrategy, MyAnalyzer
from backtester.bt_runners.etf_opengap_entry import run_bt
from backtester.analyzers.portfolio import MyAnalyzer
from backtester.strategies.etf_opengap_entry import ETFOpengapStrategy
from backtester.config.settings import PathConfig

config = PathConfig()
path = Path(config.path_to_etf_data).expanduser()
df = pd.read_csv(path, parse_dates=["Date"])

data = bt.feeds.PandasData(dataname=df.set_index("Date"),
                           fromdate=datetime.datetime(2011, 3, 1),
                           todate=datetime.datetime(2011, 5, 1))
cerebro = run_bt(data, Strategy=ETFOpengapStrategy, Analyzer=MyAnalyzer)
