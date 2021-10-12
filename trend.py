from typing import List

from abstractTrend import AbstractTrend
from abstractTrend import AbstractTrendListener
from abstractTrend import SimpleTrendImpl
from base import CzscPoint
from base import DirectType
from maincenter import MainCenter


class Trend(SimpleTrendImpl):
    """
    走势类型
    走势包含趋势和盘整，均有方向，包含大于一个中枢为趋势
    """

    def __init__(self, start: CzscPoint, end: CzscPoint, direct: DirectType, main_centers: List[MainCenter]):
        super().__init__(start, end, direct)
        self.main_centers: List[MainCenter] = main_centers


class TrendBuilder:

    def __init__(self, listeners: List[AbstractTrendListener]):
        self.listeners = listeners

    # todo


if __name__ == '__main__':
    t = Trend(CzscPoint(None,None), CzscPoint(None,None),DirectType.DOWN,[])
    print()