from abc import abstractmethod
from typing import List

from base import CzscPoint
from base import DirectType
from quote import QuoteEventListener, Quote, QuoteLevel


class Drawing:
    def __init__(self, start: CzscPoint, end: CzscPoint):
        self.start = start
        self.end = end
        self.direct = DirectType.UP if start.value() < end.value() else DirectType.DOWN


class DrawingEventListener:

    @abstractmethod
    def receiveNewDrawing(self, drawing: Drawing):
        """
        接收新一笔成立事件
        笔终点可能会通过updateLatestDrawingEndPoint更新终点，起点和方向不会变
        保证新一笔起点为上一笔终点
        :param drawing: 笔对象
        :return:
        """

        pass

    @abstractmethod
    def updateLatestDrawingEndPoint(self, drawing: Drawing):
        """
        更新最后通过receiveNewDrawing接收笔的终点
        :param drawing: 笔对象
        :return:
        """
        pass


class DrawingBuilder(QuoteEventListener):

    def __init__(self, raw_level: QuoteLevel, listeners: List[DrawingEventListener] = list()):

        self.raw_level = raw_level
        self.drawing_points: List[CzscPoint] = []

        # 已经满足笔条件，但下一笔未出现，无法确定笔结束的行情
        self.already_drawing_quotes: List[Quote] = []
        self.already_drawing_quotes_direct: DirectType = None

        # 没有延续already_drawing_quotes方向新高/新低的行情，但尚未构成一笔
        self.uncertain_drawing_quotes: List[Quote] = []
        # already_drawing_quotes后反向的极值
        self.uncertain_drawing_extremum = None
        # already_drawing_quotes后反向极值创新数
        self.uncertain_drawing_continues_extremum_count = None

        # listeners
        self.listeners: List[DrawingEventListener] = listeners

    def receiveRawQuote(self, quote: Quote, level: QuoteLevel):
        if level is not self.raw_level:
            raise BaseException("invalid quote level {} for rawLevel {}", level, self.raw_level)
        self.uncertain_drawing_quotes.append(quote)
        # 尚未形成任何笔结构
        if len(self.already_drawing_quotes) == 0:
            uncertain_len = len(self.uncertain_drawing_quotes)
            if uncertain_len < AT_LEAST_DRAWING_QUOTE_NUM:
                return
            # 是否向上一笔
            if self.uncertain_drawing_quotes[-1].high > self.uncertain_drawing_quotes[-2].high:
                for i in range(0, uncertain_len - AT_LEAST_DRAWING_QUOTE_NUM + 1):
                    new_high_count = 0
                    cur = i
                    while cur < uncertain_len - 1:
                        n = cur + 1
                        while n < uncertain_len and \
                                self.uncertain_drawing_quotes[n].high <= self.uncertain_drawing_quotes[cur].high:
                            n += 1
                        if not n < uncertain_len:
                            break
                        new_high_count += 1
                        cur = n
                    if new_high_count >= AT_LEAST_DRAWING_QUOTE_NUM - 1:
                        self.already_drawing_quotes = self.uncertain_drawing_quotes[i:]
                        self.uncertain_drawing_quotes.clear()
                        self.already_drawing_quotes_direct = DirectType.UP
                        self.uncertain_drawing_extremum = quote.low
                        self.uncertain_drawing_continues_extremum_count = 1
                        self.append_drawing_point(CzscPoint(PointType.BOTTOM, self.already_drawing_quotes[0]))
                        self.append_drawing_point(CzscPoint(PointType.TOP, self.already_drawing_quotes[-1]))
                        return
            # 是否向下一笔
            elif self.uncertain_drawing_quotes[-1].high < self.uncertain_drawing_quotes[-2].high:
                for i in range(0, uncertain_len - AT_LEAST_DRAWING_QUOTE_NUM + 1):
                    new_low_count = 0
                    cur = i
                    while cur < uncertain_len - 1:
                        n = cur + 1
                        while n < uncertain_len and \
                                self.uncertain_drawing_quotes[n].low >= self.uncertain_drawing_quotes[cur].low:
                            n += 1
                        if not n < uncertain_len:
                            break
                        new_low_count += 1
                        cur = n
                    if new_low_count >= AT_LEAST_DRAWING_QUOTE_NUM - 1:
                        self.already_drawing_quotes = self.uncertain_drawing_quotes[i:]
                        self.uncertain_drawing_quotes.clear()
                        self.already_drawing_quotes_direct = DirectType.DOWN
                        self.uncertain_drawing_extremum = quote.high
                        self.uncertain_drawing_continues_extremum_count = 1
                        self.append_drawing_point(CzscPoint(PointType.TOP, self.already_drawing_quotes[0]))
                        self.append_drawing_point(CzscPoint(PointType.BOTTOM, self.already_drawing_quotes[-1]))
                        return

        # 已存在成型一笔（该笔未确定结束）
        # 若延续已存在一笔则将uncertain归入already
        # 否则记录反向新创极值及次数，次数超过AT_LEAST_DRAWING_QUOTE_NUM则反向一笔形成
        # 标志already结束，记录already尾端点，uncertain变为already
        else:
            if self.already_drawing_quotes_direct is DirectType.UP:
                if quote.high > self.already_drawing_quotes[-1].high:
                    self.already_drawing_quotes.extend(self.uncertain_drawing_quotes)
                    self.uncertain_drawing_quotes.clear()
                    self.uncertain_drawing_extremum = quote.low
                    self.uncertain_drawing_continues_extremum_count = 1
                    self.update_drawing_point(CzscPoint(PointType.TOP, quote))
                else:
                    if quote.low < self.uncertain_drawing_extremum:
                        self.uncertain_drawing_extremum = quote.low
                        self.uncertain_drawing_continues_extremum_count += 1
                    if self.uncertain_drawing_continues_extremum_count >= AT_LEAST_DRAWING_QUOTE_NUM:
                        self.append_drawing_point(CzscPoint(PointType.BOTTOM, self.uncertain_drawing_quotes[-1]))
                        self.already_drawing_quotes = self.uncertain_drawing_quotes[:]
                        self.already_drawing_quotes_direct = DirectType.DOWN
                        self.uncertain_drawing_quotes.clear()
                        self.uncertain_drawing_extremum = quote.high
                        self.uncertain_drawing_continues_extremum_count = 1

            elif self.already_drawing_quotes_direct is DirectType.DOWN:
                if quote.low < self.already_drawing_quotes[-1].low:
                    self.already_drawing_quotes.extend(self.uncertain_drawing_quotes)
                    self.uncertain_drawing_quotes.clear()
                    self.uncertain_drawing_extremum = quote.high
                    self.uncertain_drawing_continues_extremum_count = 1
                    self.update_drawing_point(CzscPoint(PointType.BOTTOM, quote))
                else:
                    if quote.high > self.uncertain_drawing_extremum:
                        self.uncertain_drawing_extremum = quote.high
                        self.uncertain_drawing_continues_extremum_count += 1
                    if self.uncertain_drawing_continues_extremum_count >= AT_LEAST_DRAWING_QUOTE_NUM:
                        self.append_drawing_point(CzscPoint(PointType.TOP, self.uncertain_drawing_quotes[-1]))
                        self.already_drawing_quotes = self.uncertain_drawing_quotes[:]
                        self.already_drawing_quotes_direct = DirectType.UP
                        self.uncertain_drawing_quotes.clear()
                        self.uncertain_drawing_extremum = quote.low
                        self.uncertain_drawing_continues_extremum_count = 1

    def append_drawing_point(self, point: CzscPoint):
        self.drawing_points.append(point)
        if len(self.drawing_points) >= 2:
            for listener in self.listeners:
                listener.receiveNewDrawing(Drawing(self.drawing_points[-2], self.drawing_points[-1]))

    def update_drawing_point(self, point: CzscPoint):
        self.drawing_points[-1] = point
        if len(self.drawing_points) >= 2:
            for listener in self.listeners:
                listener.updateLatestDrawingEndPoint(Drawing(self.drawing_points[-2], self.drawing_points[-1]))
