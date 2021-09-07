from enum import Enum
from quote import Quote
from quote import QuoteLevel
from datetime import datetime
from typing import List

# 缠论笔/段顶点类型：高点/低点
class PointType(Enum):
    TOP = 'top'
    BOTTOM = 'bottom'


# 缠论笔/段/走势方向：上/下
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


# 缠论中枢
class MainCenter:
    def __init__(self, start: datetime, end: datetime, top: float, bottom: float):
        self.start = start
        self.end = end
        self.top = top
        self.bottom = bottom

    def print(self):
        print("maincenter from " + str(self.start) + " to " + str(self.end) +
              " top " + str(self.top) + " bottom " + str(self.bottom))


def build_maincenter_from_points(points: List[CzscPoint]):
    return MainCenter(
        points[0].quote.timestamp,
        points[-1].quote.timestamp,
        min([point.value() for point in points if point.point_type is PointType.TOP]),
        max([point.value() for point in points if point.point_type is PointType.BOTTOM])
    )

