import pyecharts.options as opts
from pyecharts.charts import Candlestick
from pyecharts.charts import Line
from quote import *
from jq import *
from structure import *
from talib import MACD


def show_czsc(name: str, contract, levels: [QuoteLevel]):
    quotes = get_all_quotes(contract, levels[0])
    macd =  MACD()
    czsc = Czsc(quotes, levels[0], levels)
    # raw quotes candle
    x_data = [quote.timestamp for quote in quotes]
    y_data = [[quote.open, quote.close, quote.low, quote.high] for quote in quotes]
    candle = Candlestick(init_opts=opts.InitOpts(width="1300px", height="600px"))
    candle.add_xaxis(xaxis_data=x_data)
    candle.add_yaxis(series_name="raw_quotes_"+levels[0].label, y_axis=y_data)
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

    # show
    candle.render(name)


if __name__ == '__main__':
    show_czsc('IH8888-30m.html', 'IH8888', [FIVE_MINUTE, THIRTY_MINUTE])
