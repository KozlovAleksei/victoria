from pandas import DataFrame


def get_previous_candle_close(symbol, interval, client):
    # Установка лимита в 2, чтобы получить две последние свечи
    df = DataFrame(client.klines(symbol, interval, limit=2))
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                  'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore']
    if len(df) > 1:
        return float(df['close'].iloc[0])  # Возвращение значения закрытия предпоследней свечи
    else:
        return None
