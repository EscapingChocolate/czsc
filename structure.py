from typing import Dict

from czsc.jq import get_quotes
from czsc.quote import *

# 构成一笔最少新高/新低行情数量
AT_LEAST_DRAWING_QUOTE_NUM = 5
# 构成一段至少3笔，即4个笔顶点
AT_LEAST_SEGMENT_DRAWING_NUM = 4


# 缠论笔/段顶点类型：高点/低点
class PointType(Enum):
    TOP = 'top'
    BOTTOM = 'bottom'


# 缠论笔/段方向：上/下
class DirectType(Enum):
    UP = 'up'
    DOWN = 'down'


# 缠论笔段顶点
class CzscPoint:
    def __init__(self, point_type: PointType, quote: Quote):
        self.point_type = point_type
        self.quote = quote

    def print(self):
        print(str(self.quote.timestamp) + ": " + str(self.point_type) + ": " +
              str(self.quote.high if self.point_type is PointType.TOP else self.quote.low))

    def value(self):
        return self.quote.high if self.point_type is PointType.TOP else self.quote.low


class AlreadySegmentEventListener:
    def __init__(self):
        self.trading_points: List[CzscPoint] = []

    def receive(self, point: CzscPoint):
        self.trading_points.append(point)


# 缠论中枢
class MainCenter:
    def __init__(self, start: datetime, end: datetime, top: float, bottom: float):
        self.start = start
        self.end = end
        self.top = top
        self.bottom = bottom


class CzscMainCenter:
    def __init__(self):
        self.top


class Czsc:

    def __init__(self, raw_quotes: List[Quote], raw_level: QuoteLevel, required_levels: List[QuoteLevel]):

        # 原始行情level，也是构成笔的level
        self.raw_level = raw_level
        # 已经确定的笔顶点
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

        # segments
        self.required_levels = required_levels
        self.segments: Dict[QuoteLevel, List[CzscPoint]] = {level: [] for level in required_levels}
        self.already_segment_points: Dict[QuoteLevel, List[CzscPoint]] = {level: [] for level in required_levels}
        self.uncertain_segment_points: Dict[QuoteLevel, List[CzscPoint]] = {level: [] for level in required_levels}
        self.already_segment_direct: Dict[QuoteLevel, DirectType] = {level: None for level in required_levels}
        self.already_segment_2nd_extreme: Dict[QuoteLevel, float] = {level: None for level in required_levels}
        self.already_segment_listener: Dict[QuoteLevel, AlreadySegmentEventListener] \
            = {level: AlreadySegmentEventListener() for level in  required_levels}

        for quote in raw_quotes:
            self.handle_single_quote(quote)

    # 处理单k线，触发笔段更新
    def handle_single_quote(self, quote: Quote):
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
                else:
                    if quote.low < self.uncertain_drawing_extremum:
                        self.uncertain_drawing_extremum = quote.low
                        self.uncertain_drawing_continues_extremum_count += 1
                    if self.uncertain_drawing_continues_extremum_count >= AT_LEAST_DRAWING_QUOTE_NUM:
                        self.append_drawing_point(CzscPoint(PointType.TOP, self.already_drawing_quotes[-1]))
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
                else:
                    if quote.high > self.uncertain_drawing_extremum:
                        self.uncertain_drawing_extremum = quote.high
                        self.uncertain_drawing_continues_extremum_count += 1
                    if self.uncertain_drawing_continues_extremum_count >= AT_LEAST_DRAWING_QUOTE_NUM:
                        self.append_drawing_point(CzscPoint(PointType.BOTTOM, self.already_drawing_quotes[-1]))
                        self.already_drawing_quotes = self.uncertain_drawing_quotes[:]
                        self.already_drawing_quotes_direct = DirectType.UP
                        self.uncertain_drawing_quotes.clear()
                        self.uncertain_drawing_extremum = quote.low
                        self.uncertain_drawing_continues_extremum_count = 1

    def get_drawings(self):
        drawings = self.drawing_points[:]
        if len(self.already_drawing_quotes) > 0:
            drawings.append(
                CzscPoint(PointType.TOP if self.already_drawing_quotes_direct is DirectType.UP else PointType.BOTTOM,
                          self.already_drawing_quotes[-1]))
        return drawings

    # 打印笔
    def print_drawings(self):
        for drawing_point in self.drawing_points:
            drawing_point.print()
        if len(self.already_drawing_quotes) > 0:
            CzscPoint(PointType.TOP if self.already_drawing_quotes_direct is DirectType.UP else PointType.BOTTOM,
                      self.already_drawing_quotes[-1]).print()

    # 增加新的笔顶点，同时更新该级别段
    def append_drawing_point(self, point: CzscPoint):
        self.drawing_points.append(point)
        self.handle_drawing(point, self.raw_level)

    # 增加新的段顶点，同时以该级别段为别笔更新高一级别
    def append_segment_point(self, point: CzscPoint, level: QuoteLevel):
        self.segments[level].append(point)
        if level is not self.required_levels[-1]:
            self.handle_drawing(point, level.next_level)

    # 处理level级别新确定的一笔，若生成段则迭代更高级别
    def handle_drawing(self, point: CzscPoint, level: QuoteLevel):
        if level is None:
            return
        self.uncertain_segment_points[level].append(point)
        # 尚无已成立段结构形成
        if len(self.already_segment_points[level]) == 0:
            uncertain_length = len(self.uncertain_segment_points[level])
            for i in range(uncertain_length - AT_LEAST_SEGMENT_DRAWING_NUM, -1, -2):
                values = [point.value() for point in self.uncertain_segment_points[level][i:]]
                if point.point_type is PointType.TOP \
                        and point.value() is max(values) \
                        and self.uncertain_segment_points[level][i].value() is min(values):
                    self.already_segment_points[level] = self.uncertain_segment_points[level][i:]
                    self.already_segment_direct[level] = DirectType.UP
                    self.already_segment_2nd_extreme[level] = max(values[:-1])
                    self.append_segment_point(self.uncertain_segment_points[level][i], level)
                    self.uncertain_segment_points[level].clear()
                    break
                elif point.point_type is PointType.BOTTOM \
                        and point.value() is min(values) \
                        and self.uncertain_segment_points[level][i].value() is max(values):
                    self.already_segment_points[level] = self.uncertain_segment_points[level][i:]
                    self.already_segment_direct[level] = DirectType.DOWN
                    self.already_segment_2nd_extreme[level] = min(values[:-1])
                    self.append_segment_point(self.uncertain_segment_points[level][i], level)
                    self.uncertain_segment_points[level].clear()
                    self.already_segment_listener[level].receive(point)
                    break
        # 已存在段结构
        else:
            uncertain_segment_values = [point.value() for point in self.uncertain_segment_points[level]]
            # 已存在向上
            if self.already_segment_direct[level] is DirectType.UP:
                # 延续
                if point.point_type is PointType.TOP and point.value() > self.already_segment_points[level][-1].value():
                    self.already_segment_2nd_extreme[level] = self.already_segment_points[level][-1].value()
                    self.already_segment_points[level].extend(self.uncertain_segment_points[level])
                    self.uncertain_segment_points[level].clear()
                # 破坏 下上下且破二高
                elif point.point_type is PointType.BOTTOM \
                        and len(uncertain_segment_values) >= AT_LEAST_SEGMENT_DRAWING_NUM - 1 \
                        and point.value() <= uncertain_segment_values[-3] \
                        and point.value() < self.already_segment_2nd_extreme[level]:
                    self.append_segment_point(self.already_segment_points[level][-1], level)
                    self.already_segment_points[level] = self.uncertain_segment_points[level][:]
                    self.already_segment_2nd_extreme[level] = \
                        min([x for x in uncertain_segment_values if x >= point.value()])
                    self.already_segment_direct[level] = DirectType.DOWN
                    self.uncertain_segment_points[level].clear()
                    self.already_segment_listener[level].receive(point)
            # 已存在向下
            else:
                # 延续
                if point.point_type is PointType.BOTTOM and point.value() < \
                        self.already_segment_points[level][-1].value():
                    self.already_segment_2nd_extreme[level] = self.already_segment_points[level][-1].value()
                    self.already_segment_points[level].extend(self.uncertain_segment_points[level])
                    self.uncertain_segment_points[level].clear()
                # 标准破坏
                elif point.point_type is PointType.TOP \
                        and len(uncertain_segment_values) >= AT_LEAST_SEGMENT_DRAWING_NUM - 1 \
                        and point.value() >= uncertain_segment_values[-3] \
                        and point.value() > self.already_segment_2nd_extreme[level]:
                    self.append_segment_point(self.already_segment_points[level][-1], level)
                    self.already_segment_points[level] = self.uncertain_segment_points[level][:]
                    self.already_segment_2nd_extreme[level] = \
                        max([x for x in uncertain_segment_values if x <= point.value()])
                    self.already_segment_direct[level] = DirectType.UP
                    self.uncertain_segment_points[level].clear()
                    self.already_segment_listener[level].receive(point)

    def get_segments(self, level: QuoteLevel):
        segments = self.segments[level][:]
        if len(self.already_segment_points[level]) > 0:
            segments.append(self.already_segment_points[level][-1])
        return segments

    def print_segments(self, level: QuoteLevel):
        print("segment points level " + level.label)
        for p in self.segments[level]:
            p.print()
        if len(self.already_segment_points[level]) > 0:
            self.already_segment_points[level][-1].print()


if __name__ == '__main__':
    quotes = get_quotes('IH8888', datetime.now(), 10000, FIVE_MINUTE)
    czsc3 = Czsc(quotes, FIVE_MINUTE, [FIVE_MINUTE, THIRTY_MINUTE, ONE_DAY])
    czsc3.print_drawings()
    czsc3.print_segments(THIRTY_MINUTE)
    czsc3.print_segments(ONE_DAY)
