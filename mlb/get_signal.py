from pandas import DataFrame


def get_signal(symbol, interval, cl):

    # def format_timestamp(timestamp):
    #     microseconds = (timestamp % 1000) * 1000
    #     datetime_obj = datetime.datetime.fromtimestamp(timestamp // 1000).replace(microsecond=microseconds)
    #     formatted_datetime = datetime_obj.strftime('%d.%m.%Y %H:%M:%S')
    #     return formatted_datetime

    limit = 298  # лимит для вычисления сигнала
    r = cl.klines(symbol, interval, limit=limit)
    df = DataFrame(r).iloc[:, :7]
    df.columns = list("bohlcve")
    # df['b'] = df['b'].apply(format_timestamp)
    # df['e'] = df['e'].apply(format_timestamp)
    df['ma_fast'] = df['c'].ewm(span=12, adjust=False).mean()
    df['ma_slow'] = df['c'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    return df.iloc[-1]
