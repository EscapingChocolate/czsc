from typing import List

from abstractTrend import AbstractTrend
from abstractTrend import AbstractTrendListener
from base import CzscPoint
from base import DirectType
from maincenter import MainCenter


class Trend(AbstractTrend):
    """
    走势类型
    走势包含趋势和盘整，均有方向，包含大于一个中枢为趋势
    """

    def __init__(self, start: CzscPoint, end: CzscPoint, direct: DirectType, main_centers: List[MainCenter]):
        self.start = start
        self.end = end
        self.direct = direct

    def start(self) -> CzscPoint:
        return self.start

    def end(self) -> CzscPoint:
        return self.end

    def direct(self) -> DirectType:
        return self.direct


class TrendBuilder:

    def __init__(self, listeners: List[AbstractTrendListener]):
        self.listeners = listeners

    # todo