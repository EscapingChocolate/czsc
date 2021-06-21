import datetime
import pandas as pd
from czsc.quote import Quote
from czsc.quote import QuoteLevel
from jqdatasdk import *


def get_quotes(contract, end_time: datetime.datetime, count: int, level: QuoteLevel):
    contract = normalize_code(contract)
    quote_list = list()
    df = get_price(contract, end_date=end_time, frequency=level.label, count=count, skip_paused=True, fill_paused=False)
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


def get_main_quote(type, end_time: datetime.datetime, count: int, level: QuoteLevel):
    contract = get_dominant_future(type)
    return get_quotes(contract, end_time, count, level)


if __name__ == '__main__':
    quotes = get_main_quote('IH', datetime.datetime.now(), 100)
    print(quotes)
