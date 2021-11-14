import pyecharts.options as opts
from pyecharts.charts import Candlestick
from pyecharts.charts import Line
from pyecharts.charts import EffectScatter
from pyecharts.globals import SymbolType
from quote import *
from listener import ThirdTradeTrader
from jq import *
from structure import *
from talib import MACD
from drawing import DrawingEventListener

def show_drawings(name: str, contract, level: QuoteLevel):
    quotes, _ = get_all_quotes(contract, level)
    x_data = [quote.timestamp for quote in quotes]
    y_data = [[quote.open, quote.close, quote.low, quote.high] for quote in quotes]
    candle = Candlestick(init_opts=opts.InitOpts(width="1300px", height="600px"))
    candle.add_xaxis(xaxis_data=x_data)
    candle.add_yaxis(series_name="raw_quotes_" + levels[0].label, y_axis=y_data)
    candle.set_series_opts()
    candle.set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        datazoom_opts=[opts.DataZoomOpts(type_="inside")],
        title_opts=opts.TitleOpts(title="Kline-ItemStyle"),
    )


def show_czsc(name: str, contract, levels: [QuoteLevel]):
    quotes, raw_df = get_all_quotes(contract, levels[0])
    # macd =  MACD()
    traders = [ThirdTradeTrader(FIVE_MINUTE), ThirdTradeTrader(THIRTY_MINUTE)]
    czsc = Czsc(quotes, levels[0], levels, traders, traders, traders)
    # raw quotes candle
    x_data = [quote.timestamp for quote in quotes]
    y_data = [[quote.open, quote.close, quote.low, quote.high] for quote in quotes]
    candle = Candlestick(init_opts=opts.InitOpts(width="1300px", height="600px"))
    candle.add_xaxis(xaxis_data=x_data)
    candle.add_yaxis(series_name="raw_quotes_" + levels[0].label, y_axis=y_data)
    candle.set_series_opts()
    candle.set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        datazoom_opts=[opts.DataZoomOpts(type_="inside")],
        title_opts=opts.TitleOpts(title="Kline-ItemStyle"),
    )

    # czsc drawing lines
    drawings = czsc.get_drawings()
    line = Line()
    x_drawing = [p.quote.timestamp for p in drawings]
    y_drawing = [p.value() for p in drawings]
    line.add_xaxis(xaxis_data=x_drawing)
    line.add_yaxis(series_name=czsc.raw_level.label + "_draw", y_axis=y_drawing)
    candle.overlap(line)

    # czsc segments
    for level in levels:
        segments = czsc.get_segments(level)
        segment_line = Line()

        x_segment = [p.quote.timestamp for p in segments]
        y_segment = [p.value() for p in segments]
        segment_line.add_xaxis(xaxis_data=x_segment)
        segment_line.add_yaxis(series_name=level.label, y_axis=y_segment)
        candle.overlap(segment_line)

    for trader in traders:
        trading_point_chart_bottom = EffectScatter()
        trading_point_chart_bottom.add_xaxis(
            [point.quote.timestamp for point in trader.open_points if point.point_type is PointType.BOTTOM])
        trading_point_chart_bottom.add_yaxis(trader.level.label + "_trade",
                                             [point.value() for point in trader.open_points if
                                              point.point_type is PointType.BOTTOM],
                                             symbol=SymbolType.TRIANGLE)
        candle.overlap(trading_point_chart_bottom)
        trading_point_chart_top = EffectScatter()
        trading_point_chart_top.add_xaxis(
            [point.quote.timestamp for point in trader.open_points if point.point_type is PointType.TOP])
        trading_point_chart_top.add_yaxis(trader.level.label + "_trade",
                                          [point.value() for point in trader.open_points if
                                           point.point_type is PointType.TOP],
                                          symbol=SymbolType.ARROW)
        candle.overlap(trading_point_chart_top)
        close_point_chart = EffectScatter()
        close_point_chart.add_xaxis([point.quote.timestamp for point in trader.close_points])
        close_point_chart.add_yaxis(trader.level.label + "_trade", [point.value() for point in trader.close_points])
        candle.overlap(close_point_chart)

    # maincenters
    for level in levels:
        maincenters = czsc.get_maincenters(level)
        for maincenter in maincenters:
            rectangle = Line()
            x = [maincenter.get_start, maincenter.get_end, maincenter.get_end, maincenter.get_start, maincenter.get_start]
            y = [maincenter.bottom, maincenter.bottom, maincenter.top, maincenter.top, maincenter.bottom]
            rectangle.add_xaxis(xaxis_data=x)
            rectangle.add_yaxis(y_axis=y, series_name="maincenter_" + level.label)
            candle.overlap(rectangle)

    # show
    candle.render(name)


if __name__ == '__main__':
    show_czsc('RB8888-30m.html', 'RB8888', [ONE_MINUTE, FIVE_MINUTE, THIRTY_MINUTE])
