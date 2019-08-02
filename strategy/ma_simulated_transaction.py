import pandas as pd
import numpy as np
import datetime
import talib

# 显示所有列
pd.set_option('display.max_columns', None)
# # 显示所有行
# pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)


class BackTesting:
    def __init__(self, slow, fast, path, trade_log_path, start_money):
        self.path = path  # 读取日线数据路径
        self.position = 0
        self.close_list = []
        self.slow_line = slow
        self.fast_line = fast
        self.start_money = start_money
        self.trade_log_path = trade_log_path   # 交易结果保存路径

    def load_data(self):
        """加载数据"""
        info = 'action,price,amount,datetime\n'
        with open(self.trade_log_path, 'a') as f:
            f.write(info)
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
        # print(ma5, ma20, dt)
        # MA
        volume = self.start_money / bar.close  # 计算下单的数量
        long_status = ma5 > ma20
        short_status = ma5 < ma20
        if long_status:
            if self.position < 0:
                self.cover(bar.close, abs(self.position), dt)
                self.buy(bar.close, volume, dt)
            elif self.position == 0:
                self.buy(bar.close, volume, dt)
        elif short_status:
            if self.position > 0:
                self.sell(bar.close, abs(self.position), dt)
                self.short(bar.close, volume, dt)
            elif self.position == 0:
                self.short(bar.close, volume, dt)

        self.close_list = self.close_list[1:]

    def buy(self, price, num, dt):
        """price:开仓价格  num:开仓手数"""
        self.position += num
        self.trade_log('buy', price, num, dt)

    def sell(self, price, num, dt):
        self.position -= num
        self.trade_log('sell', price, num, dt)

    def short(self, price, num, dt):
        self.position -= num
        self.trade_log('short', price, num, dt)

    def cover(self, price, num, dt):
        self.position += num
        self.trade_log('cover', price, num, dt)

    def trade_log(self, direction, price, num, dt):
        """记录下单情况"""
        info = direction+','+str(price)+','+str(num)+','+dt+'\n'
        with open(self.trade_log_path, 'a') as f:
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
    ma_bt = BackTesting(slow=20, fast=5, path = 'data/huobip_btc_usdt.csv', trade_log_path = 'result/ma_trade_log.csv', start_money=10000.0)
    ma_bt.start()
