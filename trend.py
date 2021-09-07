from abc import abstractmethod

from base import CzscPoint


# 走势定义类，记录从start至end的走势
class Trend:

    def __init__(self, start: CzscPoint, end: CzscPoint):
        self.start = start
        self.end = end


# 走势事件监听器
class TrendListener:

    # 接收新趋势成立事件
    @abstractmethod
    def receiveNewTrend(self, trend: Trend):
        pass

    # 更新上次成立趋势终点
    @abstractmethod
    def updateLatestTrend(self, point: CzscPoint):
        pass


class TrendBuilder:

    def __init__(self):
        # todo
        return
