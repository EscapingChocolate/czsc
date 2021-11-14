from abc import abstractmethod
from typing import List

from point import CzscPoint
from point import on_direct_point
from base import DirectType
from base import PointType
from quote import QuoteEventListener, Quote, QuoteLevel
from jq import get_all_quotes

# 构成一笔最少新高/新低行情数量
AT_LEAST_DRAWING_QUOTE_NUM = 5


class Drawing:
    """
    缠论笔
    """

    def __init__(self, start: CzscPoint, end: CzscPoint):
        self.start = start
        self.end = end
        self.direct = DirectType.UP if start.value() < end.value() else DirectType.DOWN


class DrawingEventListener:

    @abstractmethod
    def receive_new_drawing(self, point: CzscPoint):
        """
        接收新成立笔顶点事件
        笔顶点可能会通过updateLatestDrawingEndPoint更新
        保证新一笔起点为上一笔终点
        :param point: 笔顶点
        :return:
        """

        pass

    @abstractmethod
    def update_latest_drawing_end_point(self, point: CzscPoint):
        """
        更新最后通过receiveNewDrawing接收笔顶点
        :param point: 笔顶点
        :return:
        """
        pass


class DrawingStorage(DrawingEventListener):

    def __init__(self):
        self.drawings: List[CzscPoint] = []

    def receive_new_drawing(self, point: CzscPoint):
        self.drawings.append(point)

    def update_latest_drawing_end_point(self, point: CzscPoint):
        self.drawings[-1] = point


class DrawingBuilder(QuoteEventListener):
    """
    缠论笔构造器
    按照缠论原文，需要先找分型然后处理包含关系，再构成笔，较为复杂
    理论上，以上步骤和5根k线新高/低逻辑等价，遂使用此方式构造笔
    """

    def __init__(self, raw_level: QuoteLevel, listeners: List[DrawingEventListener] = list()):

        self.raw_level = raw_level
        self.drawing_points: List[CzscPoint] = []

        # 已经满足笔条件，但下一笔未出现，无法确定笔结束的行情
        self.already_drawing_quotes: List[Quote] = []
        self.already_drawing_quotes_direct: DirectType = None

        # 没有延续already_drawing_quotes方向新高/新低的行情，但尚未构成一笔
        self.uncertain_drawing_quotes: List[Quote] = []
        # already_drawing_quotes后反向的极值行情
        self.uncertain_drawing_extremum: Quote = None
        # already_drawing_quotes后反向极值创新数
        self.uncertain_drawing_continues_extremum_count = None

        # listeners
        self.listeners: List[DrawingEventListener] = listeners

    def receive_raw_quote(self, quote: Quote, level: QuoteLevel):
        """
        接收行情，生成笔并通知DrawingEventListener
        :param quote:
        :param level:
        :return:
        """
        if level is not self.raw_level:
            raise BaseException("invalid quote level {} for rawLevel {}", level, self.raw_level)
        self.uncertain_drawing_quotes.append(quote)
        # 尚未形成任何笔结构
        if len(self.already_drawing_quotes) == 0:
            uncertain_len = len(self.uncertain_drawing_quotes)
            if uncertain_len < AT_LEAST_DRAWING_QUOTE_NUM:
                return
            assume_direct = DirectType.UP if self.uncertain_drawing_quotes[-1].high > self.uncertain_drawing_quotes[
                -2].high else DirectType.DOWN
            for i in range(0, uncertain_len - AT_LEAST_DRAWING_QUOTE_NUM + 1):
                direct_continous_count = 0
                cur = i
                while cur < uncertain_len - 1:
                    n = cur + 1
                    while n < uncertain_len and not self.uncertain_drawing_quotes[cur].continuous(
                            self.uncertain_drawing_quotes[n], assume_direct):
                        n += 1
                    if n >= uncertain_len:
                        break
                    direct_continous_count += 1
                    cur = n
                if direct_continous_count >= AT_LEAST_DRAWING_QUOTE_NUM - 1:
                    self.already_drawing_quotes = self.uncertain_drawing_quotes[i:]
                    self.uncertain_drawing_quotes.clear()
                    self.already_drawing_quotes_direct = assume_direct
                    self.uncertain_drawing_extremum = quote
                    self.uncertain_drawing_continues_extremum_count = 1
                    self.append_drawing_point(
                        CzscPoint(PointType.BOTTOM if assume_direct is DirectType.UP else PointType.TOP,
                                  self.already_drawing_quotes[0]))
                    self.append_drawing_point(
                        CzscPoint(PointType.TOP if assume_direct is DirectType.UP else PointType.BOTTOM,
                                  self.already_drawing_quotes[-1]))
                    return

        # 已存在成型一笔（该笔未确定结束）
        # 若延续已存在一笔则将uncertain归入already
        # 否则记录反向新创极值及次数，次数超过AT_LEAST_DRAWING_QUOTE_NUM则反向一笔形成
        # 标志already结束，记录already尾端点，uncertain变为already
        else:
            if self.already_drawing_quotes[-1].continuous(quote, self.already_drawing_quotes_direct):
                self.already_drawing_quotes.extend(self.uncertain_drawing_quotes)
                self.uncertain_drawing_quotes.clear()
                self.uncertain_drawing_extremum = quote
                self.uncertain_drawing_continues_extremum_count = 1
                self.update_drawing_point(on_direct_point(quote, self.already_drawing_quotes_direct))
            else:
                if self.uncertain_drawing_extremum.continuous(quote, self.already_drawing_quotes_direct.reverse()):
                    self.uncertain_drawing_extremum = quote
                    self.uncertain_drawing_continues_extremum_count += 1
                if self.uncertain_drawing_continues_extremum_count >= AT_LEAST_DRAWING_QUOTE_NUM:
                    self.append_drawing_point(on_direct_point(self.uncertain_drawing_quotes[-1],
                                                              self.already_drawing_quotes_direct.reverse()))
                    self.already_drawing_quotes = self.uncertain_drawing_quotes[:]
                    self.already_drawing_quotes_direct = self.already_drawing_quotes_direct.reverse()
                    self.uncertain_drawing_quotes.clear()
                    self.uncertain_drawing_extremum = quote
                    self.uncertain_drawing_continues_extremum_count = 1

    def append_drawing_point(self, point: CzscPoint):
        self.drawing_points.append(point)
        for listener in self.listeners:
            listener.receive_new_drawing(point)

    def update_drawing_point(self, point: CzscPoint):
        self.drawing_points[-1] = point
        for listener in self.listeners:
            listener.update_latest_drawing_end_point(point)


if __name__ == '__main__':
    quotes, raw_df = get_all_quotes(contract, levels[0])
