from typing import List

from abstractTrend import AbstractTrendListener, SimpleTrendImpl
from point import CzscPoint
from base import DirectType
from base import PointType
from drawing import DrawingEventListener
from quote import QuoteLevel

AT_LEAST_SEGMENT_DRAWING_NUM = 4


class Segment(SimpleTrendImpl):
    """
    缠论段
    缠论由笔构成段，段作为最低级别行情的次级别走势类型，构成最低级别中枢
    因此理论上，段的行为应与走势类型一致
    """

    def __init__(self, start: CzscPoint, end: CzscPoint):
        super().__init__(start, end, DirectType.UP if start.point_type is PointType.BOTTOM else DirectType.DOWN)


class SegmentBuilder(DrawingEventListener):

    def __init__(self, accept_level: QuoteLevel, listeners: List[AbstractTrendListener] = []):
        self.segments: List[CzscPoint] = []
        self.already_segment_points: List[CzscPoint] = []
        self.uncertain_segment_points: List[CzscPoint] = []
        self.already_segment_direct: DirectType = None
        self.already_segment_2nd_extreme: CzscPoint = None
        self.listeners: List[AbstractTrendListener] = listeners

    def receive_new_drawing(self, point: CzscPoint):

        def is_segment_start(point: CzscPoint, segment_points: List[CzscPoint], direct: DirectType) -> bool:
            func = min if direct is DirectType.UP else max
            return point.value() is func([point.value() for point in segment_points])

        def is_segment_end(point: CzscPoint, segment_points: List[CzscPoint], direct: DirectType) -> bool:
            func = max if direct is DirectType.UP else min
            return point.value() is func([point.value() for point in segment_points])

        def extreme_func(direct: DirectType):
            return max if direct is DirectType.UP else min

        def extreme_point(points: List[CzscPoint], direct: DirectType) -> CzscPoint:
            values = [p.value() for p in points]
            return [p for p in points if p.value() is extreme_func(direct)(values)][0]

        self.uncertain_segment_points.append(point)
        # 尚无已成立段结构形成
        if len(self.already_segment_points) == 0:
            uncertain_length = len(self.uncertain_segment_points)
            for i in range(uncertain_length - AT_LEAST_SEGMENT_DRAWING_NUM, -1, -2):
                values = [point.value() for point in self.uncertain_segment_points[i:]]
                assume_direct = DirectType.UP if point.point_type is PointType.TOP else DirectType.DOWN
                if is_segment_end(point, self.uncertain_segment_points[i:], assume_direct) and is_segment_start(
                        self.uncertain_segment_points[i], self.uncertain_segment_points[i:], assume_direct):
                    self.already_segment_points = self.uncertain_segment_points[i:]
                    self.already_segment_direct = assume_direct
                    self.already_segment_2nd_extreme = extreme_point(self.uncertain_segment_points[i:][:-1], assume_direct)
                    self.append_segment_point(self.uncertain_segment_points[i])
                    self.append_segment_point(point)
                    self.uncertain_segment_points.clear()
                    break
        # 已存在段结构
        else:

            # 延续
            i = 0
            already_extreme: CzscPoint = None
            while i < len(self.already_segment_points) - 2:
                if self.already_segment_points[i].point_type is self.already_segment_direct.associated_point_type() \
                        and self.already_segment_points[i].continuous(self.already_segment_points[i + 2],
                                                                      self.already_segment_direct):
                    already_extreme = extreme_point(self.already_segment_points[i:], self.already_segment_direct)
                    break
                i += 1
            if point.point_type is self.already_segment_direct.associated_point_type() and (
                    already_extreme is None or already_extreme.continuous(point, self.already_segment_direct)):
                self.already_segment_2nd_extreme = already_extreme if already_extreme is not None \
                    else extreme_point(self.already_segment_points, self.already_segment_direct)
                self.already_segment_points.extend(self.uncertain_segment_points)
                self.update_segment_point(point)
                self.uncertain_segment_points.clear()
            # 破坏
            elif point.point_type is not self.already_segment_direct.associated_point_type() \
                    and len(self.uncertain_segment_points) >= AT_LEAST_SEGMENT_DRAWING_NUM - 1 \
                    and self.uncertain_segment_points[-3].continuous(point, self.already_segment_direct.reverse()) \
                    and self.already_segment_2nd_extreme.break_through(point):
                self.append_segment_point(point)
                self.already_segment_points = self.uncertain_segment_points[:]
                self.already_segment_2nd_extreme = extreme_point(self.uncertain_segment_points[:-1],
                                                                 self.already_segment_direct.reverse())
                self.already_segment_direct =  self.already_segment_direct.reverse()
                self.uncertain_segment_points.clear()
            # 已存在向下
            # else:
            #     # 延续
            #     i = 0
            #     already_min = None
            #     while i < len(self.already_segment_points) - 2:
            #         if self.already_segment_points[i].value() >= \
            #                 self.already_segment_points[i + 2].value() and \
            #                 self.already_segment_points[i].point_type is PointType.BOTTOM:
            #             already_min = min([p.value() for p in self.already_segment_points[i:]])
            #             break
            #         i += 1
            #
            #     if point.point_type is PointType.BOTTOM and (already_min is None or point.value() < already_min):
            #         self.already_segment_2nd_extreme = already_min if already_min is not None \
            #             else self.already_segment_points[-2].value()
            #         self.already_segment_points.extend(self.uncertain_segment_points)
            #         self.update_segment_point(point, level)
            #         self.uncertain_segment_points.clear()
            #     # 破坏
            #     elif point.point_type is PointType.TOP \
            #             and len(uncertain_segment_values) >= AT_LEAST_SEGMENT_DRAWING_NUM - 1 \
            #             and point.value() >= uncertain_segment_values[-3] \
            #             and point.value() > self.already_segment_2nd_extreme:
            #         self.append_segment_point(point, level)
            #         self.already_segment_points = self.uncertain_segment_points[:]
            #         self.already_segment_2nd_extreme = \
            #             max([x for x in uncertain_segment_values if x <= point.value()])
            #         self.already_segment_direct = DirectType.UP
            #         self.uncertain_segment_points.clear()

    def append_segment_point(self, point: CzscPoint):
        self.segments.append(point)
        # todo listeners

    def update_segment_point(self, point: CzscPoint):
        self.segments[-1] = point
        # todo listeners

    def update_latest_drawing_end_point(self, point: CzscPoint):
        self.backspace_drawing_in_segment()
        self.receive_new_drawing(point)

    def backspace_drawing_in_segment(self):
        uncertain_length = len(self.uncertain_segment_points)
        if uncertain_length > 0:
            self.uncertain_segment_points = self.uncertain_segment_points[:-1]
        else:
            self.already_segment_points = self.already_segment_points[:-1]
