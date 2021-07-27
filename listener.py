from abc import abstractmethod, ABCMeta
from enum import Enum
from typing import List

from base import CzscPoint
from base import MainCenter
from base import PointType
from base import build_maincenter_from_points
from quote import Quote
from quote import QuoteLevel


class QuoteListener(metaclass=ABCMeta):

    @abstractmethod
    def receiveQuote(self, quote: Quote, level: QuoteLevel):
        pass


class NewSegmentListener(metaclass=ABCMeta):

    @abstractmethod
    def receiveSegment(self, point: CzscPoint, level: QuoteLevel):
        pass


class NewMaincenterEventListener(metaclass=ABCMeta):

    @abstractmethod
    def receiveMaincenter(self, maincenter_points: List[CzscPoint], level: QuoteLevel):
        pass


class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


class TradeDirect(Enum):
    LONG = "long"
    SHORT = "short"

# todo 三买/卖 且 下级别中枢趋势同向
class ThirdTradeTrader(QuoteListener, NewSegmentListener, NewMaincenterEventListener):

    def __init__(self, level: QuoteLevel):
        self.open_points: List[CzscPoint] = []
        self.close_points: List[CzscPoint] = []
        self.last_maincenter: MainCenter = None
        self.previous_lower_maincenter: MainCenter = None
        self.current_lower_maincenter: MainCenter = None
        self.trade_status: TradeStatus = TradeStatus.CLOSED
        self.trade_direct: TradeDirect = None
        self.stop_loss_point: float = None
        self.level: QuoteLevel = level

    def receiveMaincenter(self, maincenter_points: List[CzscPoint], level: QuoteLevel):
        maincenter = build_maincenter_from_points(maincenter_points)
        if level is self.level:
            if self.trade_status is TradeStatus.CLOSED and self.last_maincenter is not None and \
                    self.last_maincenter.start is not maincenter.start:
                self.open_points.append(maincenter_points[-1])
                self.trade_status = TradeStatus.OPEN
                self.trade_direct = TradeDirect.LONG \
                    if maincenter_points[-1].point_type is PointType.TOP \
                    else TradeDirect.SHORT
                self.stop_loss_point = maincenter_points[-2].value()
                self.previous_lower_maincenter = None
            self.last_maincenter = maincenter
        elif level.next_level is self.level:
            if self.current_lower_maincenter is not None and self.current_lower_maincenter.start is not maincenter.start:
                self.previous_lower_maincenter = self.current_lower_maincenter
            self.current_lower_maincenter = maincenter;
            if self.trade_status is TradeStatus.CLOSED:
                return
            if self.previous_lower_maincenter is None:
                return
            if (self.trade_direct is TradeDirect.LONG and
                self.current_lower_maincenter.top < self.previous_lower_maincenter.bottom) \
                    or \
                    (self.trade_direct is TradeDirect.SHORT and
                     self.current_lower_maincenter.bottom > self.previous_lower_maincenter.top):
                self.close_points.append(maincenter_points[-1])
                self.trade_status = TradeStatus.CLOSED

    def receiveQuote(self, quote: Quote, level: QuoteLevel):
        if self.trade_status is TradeStatus.CLOSED:
            return
        if (self.trade_direct is TradeDirect.LONG and quote.low < self.stop_loss_point) or \
                (self.trade_direct is TradeDirect.SHORT and quote.high > self.stop_loss_point):
            self.close_points.append(
                CzscPoint(
                    PointType.BOTTOM if self.trade_direct is TradeDirect.LONG else PointType.TOP,
                    quote
                )
            )
            self.trade_status = TradeStatus.CLOSED

    def receiveSegment(self, point: CzscPoint, level: QuoteLevel):
        if not level.next_level is self.level:
            return
        if self.trade_status is TradeStatus.CLOSED:
            return
        if self.previous_lower_maincenter is None:
            return
        if (self.trade_direct is TradeDirect.LONG and point.value() < self.previous_lower_maincenter.bottom) or \
                (self.trade_direct is TradeDirect.SHORT and point.value() > self.previous_lower_maincenter.top):
            self.close_points.append(point)
            self.trade_status = TradeStatus.CLOSED
