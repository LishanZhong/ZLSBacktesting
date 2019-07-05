import pandas as pd
import numpy as np
import datetime
import talib


class BackTesting:
    def __init__(self):
        self.path = ''
        self.position = 0
        self.close_list = []
        self.slow_line = 20
        self.fast_line = 5

    def load_data(self):
        """加载数据"""
        data = pd.read_csv(self.path)
        for index, row in data.iterrows():
            bar = Bar
            bar.datetime = row.timestamp
            bar.close = row.close
            self.onBar(bar)

    def onBar(self, bar):
        """策略"""
        # 下载的数据的时间是时间戳格式，转换为看得懂的格式
        self.close_list.append(bar.close)
        if len(self.close_list) < self.slow_line:
            return
        dt = datetime.datetime.fromtimestamp(bar.datetime).strftime("%Y-%m-%d")
        ma20 = talib.MA(np.array(self.close_list, dtype=float), self.slow_line)[-1]
        ma5 = talib.MA(np.array(self.close_list, dtype=float), self.fast_line)[-1]
        print(ma5, ma20, dt)

        self.close_list = self.close_list[1:]

    def buy(self, price, num, dt):
        """price:开仓价格  num:开仓手数"""
        self.position += num
        self.trade_log('buy', price, num, dt)

    def sell(self, price, num):
        self.position -= num
        self.trade_log('sell', price, num, dt)

    def short(self, price, num):
        self.position -= num
        self.trade_log('short', price, num, dt)

    def cover(self, price, num):
        self.position += num
        self.trade_log('cover', price, num, dt)

    def trade_log(self, direction, price, num, dt):
        """记录下单情况"""
        info = direction+','+str(price)+','+str(num)+','+dt
        with open('trade_log.csv', 'a') as f:
            f.write(info)
        print(info)

    def start(self):
        self.load_data()


class Bar:
    def __init__(self):
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None
        self.datetime = None

if __name__ == '__main__':
    bt = BackTesting()
    bt.path = 'data/huobip_btc_usdt.csv'    # 读取日线数据路径
    bt.start()
