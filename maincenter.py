from abstractTrend import AbstractTrendListener


class MainCenter:

    def __init__(self, start: CzscPoint, end: CzscPoint, direct: DirectType):
        self.start = start
        self.end = end
        self.direct = direct


class MainCenterBuilder(AbstractTrendListener):

    def __init__(self):
        return

    def receive_new_trend(self, trend: Trend):
        return

    def update_latest_trend(self, point: CzscPoint):
        return
