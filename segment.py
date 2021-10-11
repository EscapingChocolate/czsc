from typing import List

from abstractTrend import AbstractTrend, AbstractTrendListener
from base import CzscPoint
from drawing import DrawingEventListener
from quote import QuoteLevel


class Segment(AbstractTrend):
    """
    缠论段
    缠论由笔构成段，段作为最低级别行情的次级别走势类型，构成最低级别中枢
    因此理论上，段的行为应与走势类型一致
    """

    def __init__(self, start: CzscPoint, end: CzscPoint):
        super(Segment, self).__init__(start, end)


class SegmentBuilder(DrawingEventListener):

    def __init__(self, accept_level: QuoteLevel, listeners: List[AbstractTrendListener]):
        self.segments: List[CzscPoint] = []
        self.already_segment_points: List[CzscPoint] = []
        self.uncertain_segment_points: List[CzscPoint] = []
        self.already_segment_direct: DirectType = None
        self.already_segment_2nd_extreme: float = None
        self.listeners: List[AbstractTrendListener] = listeners

    def receive_new_drawing(self, point: CzscPoint):
        self.uncertain_segment_points.append(point)
        # 尚无已成立段结构形成
        if len(self.already_segment_points) == 0:
            uncertain_length = len(self.uncertain_segment_points)
            for i in range(uncertain_length - AT_LEAST_SEGMENT_DRAWING_NUM, -1, -2):
                values = [point.value() for point in self.uncertain_segment_points[i:]]
                if point.point_type is PointType.TOP \
                        and point.value() is max(values) \
                        and self.uncertain_segment_points[i].value() is min(values):
                    self.already_segment_points = self.uncertain_segment_points[i:]
                    self.already_segment_direct = DirectType.UP
                    self.already_segment_2nd_extreme = max(values[:-1])
                    self.append_segment_point(self.uncertain_segment_points[i], level)
                    self.append_segment_point(point, level)
                    self.uncertain_segment_points.clear()
                    break
                elif point.point_type is PointType.BOTTOM \
                        and point.value() is min(values) \
                        and self.uncertain_segment_points[i].value() is max(values):
                    self.already_segment_points = self.uncertain_segment_points[i:]
                    self.already_segment_direct = DirectType.DOWN
                    self.already_segment_2nd_extreme = min(values[:-1])
                    self.append_segment_point(self.uncertain_segment_points[i], level)
                    self.append_segment_point(point, level)
                    self.uncertain_segment_points.clear()
                    break
        # 已存在段结构
        else:
            uncertain_segment_values = [point.value() for point in self.uncertain_segment_points]
            # 已存在向上
            if self.already_segment_direct is DirectType.UP:
                # 延续
                i = 0
                already_max = None
                while i < len(self.already_segment_points) - 2:
                    if self.already_segment_points[i].value() <= \
                            self.already_segment_points[i + 2].value() and \
                            self.already_segment_points[i].point_type is PointType.TOP:
                        already_max = max([p.value() for p in self.already_segment_points[i:]])
                        break
                    i += 1
                if point.point_type is PointType.TOP and (already_max is None or point.value() > already_max):
                    self.already_segment_2nd_extreme = already_max if already_max is not None \
                        else self.already_segment_points[-2].value()
                    self.already_segment_points.extend(self.uncertain_segment_points)
                    self.update_segment_point(point, level)
                    self.uncertain_segment_points.clear()
                # 破坏
                elif point.point_type is PointType.BOTTOM \
                        and len(uncertain_segment_values) >= AT_LEAST_SEGMENT_DRAWING_NUM - 1 \
                        and point.value() <= uncertain_segment_values[-3] \
                        and point.value() < self.already_segment_2nd_extreme:
                    self.append_segment_point(point, level)
                    self.already_segment_points = self.uncertain_segment_points[:]
                    self.already_segment_2nd_extreme = \
                        min([x for x in uncertain_segment_values if x >= point.value()])
                    self.already_segment_direct = DirectType.DOWN
                    self.uncertain_segment_points.clear()
            # 已存在向下
            else:
                # 延续
                i = 0
                already_min = None
                while i < len(self.already_segment_points) - 2:
                    if self.already_segment_points[i].value() >= \
                            self.already_segment_points[i + 2].value() and \
                            self.already_segment_points[i].point_type is PointType.BOTTOM:
                        already_min = min([p.value() for p in self.already_segment_points[i:]])
                        break
                    i += 1

                if point.point_type is PointType.BOTTOM and (already_min is None or point.value() < already_min):
                    self.already_segment_2nd_extreme = already_min if already_min is not None \
                        else self.already_segment_points[-2].value()
                    self.already_segment_points.extend(self.uncertain_segment_points)
                    self.update_segment_point(point, level)
                    self.uncertain_segment_points.clear()
                # 破坏
                elif point.point_type is PointType.TOP \
                        and len(uncertain_segment_values) >= AT_LEAST_SEGMENT_DRAWING_NUM - 1 \
                        and point.value() >= uncertain_segment_values[-3] \
                        and point.value() > self.already_segment_2nd_extreme:
                    self.append_segment_point(point, level)
                    self.already_segment_points = self.uncertain_segment_points[:]
                    self.already_segment_2nd_extreme = \
                        max([x for x in uncertain_segment_values if x <= point.value()])
                    self.already_segment_direct = DirectType.UP
                    self.uncertain_segment_points.clear()

    def update_latest_drawing_end_point(self, point: CzscPoint):
        self.backspace_drawing_in_segment(self.raw_level)
        self.receive_new_drawing(point, self.raw_level)

    def backspace_drawing_in_segment(self, level: QuoteLevel):
        uncertain_length = len(self.uncertain_segment_points)
        if uncertain_length > 0:
            self.uncertain_segment_points = self.uncertain_segment_points[:-1]
        else:
            self.already_segment_points = self.already_segment_points[:-1]
