from quote import Quote
from base import PointType
from base import DirectType


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

    def inner(self, point) -> bool:
        return point.value() < self.value() if self.point_type is PointType.TOP else point.value() > self.value()

    def outer(self, point) -> bool:
        return not self.inner(point)


def on_direct_point(quote: Quote, direct: DirectType) -> CzscPoint:
    return CzscPoint(PointType.TOP if direct is DirectType.UP else PointType.BOTTOM, quote)
