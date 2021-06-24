from datetime import datetime
import pandas as pd
from czsc.quote import *
from jqdatasdk import *
from talib import MACD


def format_quotes(df: pd.DataFrame):
    quote_list = list()
    for (time, price) in df.iterrows():
        quote_list.append(Quote(
            open_price=price['open'],
            close_price=price['close'],
            high_price=price['high'],
            low_price=price['low'],
            volume=price['volume'],
            timestamp=time
        ))
    return quote_list


def get_quotes(contract, end_time: datetime, count: int, level: QuoteLevel):
    contract = normalize_code(contract)
    df = get_price(contract, end_date=end_time, frequency=level.label, count=count, skip_paused=True, fill_paused=False)
    return format_quotes(df)


def get_all_quotes(contract, level: QuoteLevel):
    contract = normalize_code(contract)
    start_date = get_all_securities(['futures']).loc[contract]['start_date']
    df = get_price(contract, start_date=start_date,
                   end_date=datetime.now(), frequency=level.label, skip_paused=True, fill_paused=False)
    return format_quotes(df), df


def get_main_quote(type, end_time:datetime, count: int, level: QuoteLevel):
    contract = get_dominant_future(type)
    return get_quotes(contract, end_time, count, level)


if __name__ == '__main__':
    quotes, df = get_all_quotes("IH2106", THIRTY_MINUTE)
    macd = MACD(df['close'],fastperiod=12, slowperiod=26, signalperiod=9)
    print()