# backtrader_doc2
2020年以降のbacktraderの使い方に関するスクリプトまとめ。

## cheat on closeとcheat on openの使いかた
通常のbuyは、実行したバーの次のバーで買う。

    def action_buy(self):
        self.log('BUY CREATE, %.2f' % self.dataclose[0])
        # buyした次のバーのopenで買う
        # self.order = self.buy(exectype=bt.Order.Market)
        # buyした次のバーのcloseで買う
        self.order = self.buy(exectype=bt.Order.Close)

`cerebro = bt.Cerebro(stdstats=False, cheat_on_open=cheat_on_open)`
を使うと、cheat_on_openを使えるようになる。（有効化するだけ）
これでnext_openを使えるようになる。

また、`cerebro.broker.set_coc(True)`をすることでcheat_on_closeを使えるようになる。（有効化するだけ）

両方を併用できる。

実際に、これらを実行するには、以下のようにする。

cheat_on_openの場合：

    def next_open(self):
        self.order = self.buy(coo=True, coc=False)

これにより、そのbarのdataを参照しつつ、そのbarで取引できる。

cheat_on_closeの場合：

    def next(self):
        self.order = self.buy(coo=False, coc=True)
        # ここで以下のように、exectype=bt.Order.Closeとすると、通常のClose注文になるので注意
        # self.order = self.buy(coo=False, coc=True, exectype=bt.Order.Close)
        # 一方以下のように、bt.Order.Marketなら問題なく、cheat_on_closeになる
        # self.order = self.buy(coo=False, coc=True, exectype=bt.Order.Market)

これにより、そのbarのdataを参照しつつ、そのbarで取引できる。

cheatを使わない場合には、buyを実行した次のbarで取引する。
その際に、`self.order = self.buy(exectype=bt.Order.Market)`とすると、openで取引し、`self.order = self.buy(exectype=bt.Order.Close)`とすると、closeで取引する。

cheat_on_closeを有効にした状態で通常通り、次のbarのopenで買う：
`self.order = self.buy(exectype=bt.Order.Market, coc=False)`

