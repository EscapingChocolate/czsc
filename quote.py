from datetime import datetime
from enum import Enum
from typing import List


# 行情级别
class QuoteLevel:

    def __init__(self, label, next_level):
        self.label = label
        self.next_level = next_level


ONE_MONTH = QuoteLevel('1M', None)
ONE_WEEK = QuoteLevel('1w', ONE_MONTH)
ONE_DAY = QuoteLevel('1d', ONE_WEEK)
THIRTY_MINUTE = QuoteLevel('30m', ONE_DAY)
FIVE_MINUTE = QuoteLevel('5m', THIRTY_MINUTE)
ONE_MINUTE = QuoteLevel('1m', FIVE_MINUTE)


# 单k线行情，包含价格成交量及时间戳
class Quote:
    def __init__(self,
                 open_price: float,
                 close_price: float,
                 high_price: float,
                 low_price: float,
                 volume: float,
                 timestamp: datetime):
        self.open = open_price
        self.close = close_price
        self.high = high_price
        self.low = low_price
        self.vol = volume
        self.timestamp = timestamp
