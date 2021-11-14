import pyecharts.options as opts
from pyecharts.charts import Candlestick
from pyecharts.charts import Line
from pyecharts.charts import EffectScatter
from quote import *
from jq import get_all_quotes
from drawing import DrawingBuilder
from drawing import DrawingStorage


def show_drawings(name: str, contract, level: QuoteLevel):
    quotes, _ = get_all_quotes(contract, level)
    x_data = [quote.timestamp for quote in quotes]
    y_data = [[quote.open, quote.close, quote.low, quote.high] for quote in quotes]
    candle = Candlestick(init_opts=opts.InitOpts(width="1300px", height="600px"))
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
    drawing_storage = DrawingStorage()
    drawing_builder = DrawingBuilder(level, [drawing_storage])
    for quote in quotes:
        drawing_builder.receive_raw_quote(quote, level)
    drawings = drawing_storage.drawings
    line = Line()
    x_drawing = [p.quote.timestamp for p in drawings]
    y_drawing = [p.value() for p in drawings]
    line.add_xaxis(xaxis_data=x_drawing)
    line.add_yaxis(series_name=level.label + "_draw", y_axis=y_drawing)
    candle.overlap(line)
    candle.render(name)


if __name__ == '__main__':
    show_drawings("show-drawings-IH8888.html", "IH8888", ONE_DAY)
