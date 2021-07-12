import pyecharts.options as opts
from pyecharts.charts import Candlestick
from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts.charts import Grid
from pyecharts.commons.utils import JsCode
from quote import *
from jq import *
from structure import *
from talib import MACD


def show_czsc(name: str, contract, levels: [QuoteLevel]):
    quotes, raw_df = get_all_quotes(contract, levels[0])
    czsc = Czsc(quotes, levels[0], levels)
    # raw quotes candle
    x_data = [quote.timestamp for quote in quotes]
    y_data = [[quote.open, quote.close, quote.low, quote.high] for quote in quotes]
    candle = Candlestick()
    candle.add_xaxis(xaxis_data=x_data)

    candle.add_yaxis(series_name="kline",
                     y_axis=y_data,
                     itemstyle_opts=opts.ItemStyleOpts(  # 自定义颜色
                         color="#ec0000",
                         color0="#00da3c",
                         border_color="#8A0000",
                         border_color0="#008F28", )
                     )
    candle.set_global_opts(
        title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
        #    yaxis_opts=opts.AxisOpts(is_scale=True,splitarea_opts=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)),),
        yaxis_opts=opts.AxisOpts(is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)),
        #    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
        datazoom_opts=[
            opts.DataZoomOpts(is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100),
            # xaxis_index=[0, 0]设置第一幅图为内部缩放
            opts.DataZoomOpts(is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100),
            # xaxis_index=[0, 1]连接第二幅图的axis
            # opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
            # # xaxis_index=[0, 2]连接第三幅图的axis
        ],
        # 三个图的 axis 连在一块
        # axispointer_opts=opts.AxisPointerOpts(
        #     is_show=True,
        #     link=[{"xAxisIndex": "all"}],
        #     label=opts.LabelOpts(background_color="#777"),
        # ),
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

    macd =  MACD(raw_df['close'], fastperiod=34, slowperiod=200, signalperiod=13)
    macd_bar = Bar()
    macd_bar.add_xaxis(xaxis_data=x_data)
    macd_bar.add_yaxis(
        series_name="MACD",
        y_axis=list(macd[2].fillna(0)),
        xaxis_index=1, # 用于合并显示时排列位置，单独显示不要添加
        yaxis_index=1, # 用于合并显示时排列位置，单独显示不要添加
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(
            color=JsCode(
                """
                    function(params) {
                        var colorList;
                        if (params.data >= 0) {
                          colorList = '#ef232a';
                        } else {
                          colorList = '#14b143';
                        }
                        return colorList;
                    }
                    """
            )
        ),
    )
    macd_bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=1, # 用于合并显示时排列位置，单独显示不要添加
            axislabel_opts=opts.LabelOpts(is_show=False),
        ),
        yaxis_opts=opts.AxisOpts(
            grid_index=1, # 用于合并显示时排列位置，单独显示不要添加
            split_number=4,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(is_show=True),
        ),
        legend_opts=opts.LegendOpts(is_show=False),
    )

    grid_chart = Grid(init_opts=opts.InitOpts(width="1300px", height="600px"))
    grid_chart.add(
        candle,
        grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", height="60%"),
    )
    # grid_chart.add(
    #     macd_bar,
    #     grid_opts=opts.GridOpts(
    #         pos_left="3%", pos_right="1%", pos_top="75%", height="14%"
    #     ),
    # )

    # show
    grid_chart.render(name)




if __name__ == '__main__':
    show_czsc('IH8888-30m.html', 'IH2109', [ONE_MINUTE, FIVE_MINUTE])

