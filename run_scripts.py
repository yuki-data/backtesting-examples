import datetime
import backtrader as bt
from pathlib import Path
from etf_opengap import run_bt, ETFOpengapStrategy, MyAnalyzer
import pandas as pd

path = Path("~/development/data/SPDR_S&P500_ETF_2010-2020.csv").expanduser()
df = pd.read_csv(path, parse_dates=["Date"])

data = bt.feeds.PandasData(dataname=df.set_index("Date"),
                           fromdate=datetime.datetime(2011, 3, 1),
                           todate=datetime.datetime(2011, 5, 1))
cerebro = run_bt(data, Strategy=ETFOpengapStrategy, Analyzer=MyAnalyzer)
