from typing import List

from abstractTrend import AbstractTrendListener
from abstractTrend import AbstractTrend
from abstractTrend import SimpleTrendImpl
from base import DirectType
from base import CzscPoint

# 当uncertain超过5时，计最后5个走势为a1-a5
# 当a5出现，确认a4结束
# 若a4未与a2重叠，则a2无法组成中枢，将a1-a3合并处理
MERGE_CHECK_VAVLE = 5


class MainCenter:
    """
    缠论中枢，缠论定义次级别重叠三段为中枢
    本工具对所有级别进行同级别分解，不定义中枢扩展扩张
    即包括出入中枢一共5个次级别趋势，中间三段重叠，出段延续如段方向中枢成立
    """
    def __init__(self, start: CzscPoint, end: CzscPoint, direct: DirectType):
        self.start = start
        self.end = end
        self.direct = direct


class MainCenterBuilder(AbstractTrendListener):

    def __init__(self):
        self.uncertain_trends: List[AbstractTrend] = []

    def receive_new_trend(self, trend: AbstractTrend):
        self.uncertain_trends.append(trend)
        if len(self.uncertain_trends) >= MERGE_CHECK_VAVLE:
            a2: AbstractTrend = self.uncertain_trends[-4]
            a4: AbstractTrend = self.uncertain_trends[-2]
            # a2 a4未重叠合并
            if (a4.get_end() > a2.get_start() if a2.get_direct() == DirectType.DOWN else a2.get_start() > a4.get_end()):
                a1 = self.uncertain_trends[-5]
                a3 = self.uncertain_trends[-3]
                mergedTrend = SimpleTrendImpl(a1.get_start(), a3.get_end(), a1.get_direct())
                self.uncertain_trends = self.uncertain_trends[:-5]+[mergedTrend]+self.uncertain_trends[-2:]
            # 若否则检查是否存在中枢
            else:
                # todo
                pass
        return

    def update_latest_trend(self, trend: AbstractTrend):
        return
