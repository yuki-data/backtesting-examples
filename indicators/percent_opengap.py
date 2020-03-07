import backtrader as bt


class Opengap(bt.Indicator):
    params = (("gapup_threshold", 1),)
    lines = ("open_gap_up",)

    def __init__(self):
        pct_relative_open = bt.DivByZero(self.data0.lines.open - self.data0.lines.close(-1), self.data0.lines.close(-1), bt.NAN)
        self.lines.open_gap_up = (pct_relative_open * 100) > self.p.gapup_threshold
