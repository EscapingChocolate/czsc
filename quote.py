from abc import abstractmethod
from datetime import datetime


class QuoteLevel:
    """
    行情级别
    """

    def __init__(self, label, next_level):
        self.label = label
        self.next_level = next_level


ONE_MONTH = QuoteLevel('1M', None)
ONE_WEEK = QuoteLevel('1w', ONE_MONTH)
ONE_DAY = QuoteLevel('1d', ONE_WEEK)
THIRTY_MINUTE = QuoteLevel('30m', ONE_DAY)
FIVE_MINUTE = QuoteLevel('5m', THIRTY_MINUTE)
ONE_MINUTE = QuoteLevel('1m', FIVE_MINUTE)


class Quote:
    """
    单k线行情，包含价格成交量及时间戳
    """

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


class QuoteEventListener:

    @abstractmethod
    def receive_raw_quote(self, quote: Quote, level: QuoteLevel):
        """
        k线行情事件listener
        :param quote: k线
        :param level: 行情级别
        :return:
        """
        pass
