from abc import ABCMeta
from abc import abstractmethod

from base import CzscPoint
from base import DirectType


class AbstractTrend(metaclass=ABCMeta):
    """
    走势抽象
    低级别走势重叠构成中枢，中枢又生成当级别走势
    抽象无中枢引用的趋势，防止循环依赖
    """

    @abstractmethod
    def get_start(self) -> CzscPoint:
        pass

    @abstractmethod
    def get_end(self) -> CzscPoint:
        pass

    @abstractmethod
    def get_direct(self) -> DirectType:
        pass


class SimpleTrendImpl(AbstractTrend):
    """
    抽象走势简单实现
    """

    def __init__(self, start: CzscPoint, end: CzscPoint, direct: DirectType):
        self.start = start
        self.end = end
        self.direct = direct

    def get_start(self) -> CzscPoint:
        return self.start

    def get_end(self) -> CzscPoint:
        return self.end

    def get_direct(self) -> DirectType:
        return self.direct


class AbstractTrendListener:
    """
    走势事件监听器
    """

    @abstractmethod
    def receive_new_trend(self, trend: AbstractTrend):
        """
        接收新走势成立事件
        :param trend: 新成立走势
        :return:
        """
        pass

    @abstractmethod
    def update_latest_trend(self, trend: AbstractTrend):
        """
        更新上次receiveNewTrend走势终点
        :param point:
        :return:
        """
        pass
