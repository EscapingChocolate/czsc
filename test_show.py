import pyecharts.options as opts
from pyecharts.charts import Candlestick
from pyecharts.charts import Line
from pyecharts.charts import EffectScatter
from quote import *
from jq import get_all_quotes
from drawing import DrawingBuilder
from drawing import DrawingStorage
from segment import SegmentBuilder


def build_raw_quotes(candle, quotes, level):
    x_data = [quote.timestamp for quote in quotes]
    y_data = [[quote.open, quote.close, quote.low, quote.high] for quote in quotes]
    candle.add_xaxis(xaxis_data=x_data)
    candle.add_yaxis(series_name="raw_quotes_" + level.label, y_axis=y_data)
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


def build_drawings(candle, drawings, level):
    line = Line()
    x_drawing = [p.quote.timestamp for p in drawings]
    y_drawing = [p.value() for p in drawings]
    line.add_xaxis(xaxis_data=x_drawing)
    line.add_yaxis(series_name=level.label + "_draw", y_axis=y_drawing)
    candle.overlap(line)


def build_segments(candle, segments, level):
    trend_line = Line()
    x_segments = [p.quote.timestamp for p in segments]
    y_segments = [p.value() for p in segments]
    trend_line.add_xaxis(xaxis_data=x_segments)
    trend_line.add_yaxis(series_name=level.label, y_axis=y_segments)
    candle.overlap(trend_line)


def show_drawings(name: str, contract, level: QuoteLevel):
    quotes, _ = get_all_quotes(contract, level)
    candle = Candlestick(init_opts=opts.InitOpts(width="1300px", height="600px"))
    build_raw_quotes(candle, quotes, level)
    drawing_builder = DrawingBuilder(level)
    for quote in quotes:
        drawing_builder.receive_raw_quote(quote, level)
    drawings = drawing_builder.drawing_points
    build_drawings(candle, drawings, level)
    candle.render(name)


def show_segments(name: str, contract, level: QuoteLevel):
    quotes, _ = get_all_quotes(contract, level)
    candle = Candlestick(init_opts=opts.InitOpts(width="1300px", height="600px"))
    build_raw_quotes(candle, quotes, level)
    segment_builder = SegmentBuilder(level)
    drawing_builder = DrawingBuilder(level, [segment_builder])
    for quote in quotes:
        drawing_builder.receive_raw_quote(quote, level)
    drawings = drawing_builder.drawing_points
    build_drawings(candle, drawings, level)
    segments = segment_builder.segments;
    build_segments(candle, segments, level)
    candle.render(name)


if __name__ == '__main__':
    show_segments("show-drawings-IH8888.html", "IH8888", FIVE_MINUTE)
