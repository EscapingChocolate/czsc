from abc import abstractmethod

from base import CzscPoint
from base import DirectType


class AbstractTrend:
    """
    走势抽象
    低级别走势重叠构成中枢，中枢又生成当级别走势
    抽象无中枢引用的趋势，防止循环依赖
    同时段也继承该抽象，实现最低级别次级别走势
    """

    @abstractmethod
    def start(self) -> CzscPoint:
        pass

    @abstractmethod
    def end(self) -> CzscPoint:
        pass

    @abstractmethod
    def direct(self) -> DirectType:
        pass


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
