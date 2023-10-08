import requests
from pandas import DataFrame
import time

def get_symbol_data(symbol, interval, cl, base_url="https://api.binance.com", end_point="/api/v3/exchangeInfo"):


    def get_close_price(symbol, interval):
        df = DataFrame(cl.klines(symbol, interval, limit=1)).iloc[:, :6]
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        return df.iloc[-1]

    def get_gDights(gTick_size):
        str_gTick_size = str(gTick_size)
        decimal_part = str_gTick_size.split('.')[-1]  # Получение десятичной части
        return len(decimal_part.rstrip('0'))  # Получение количества значащих символов

    while True:
        try:
            result01 = get_close_price(symbol, interval)
            get_json2 = requests.get(f"{base_url}{end_point}?symbol={symbol}")
            break
        except Exception as e:
            print('Ошибка:', e)
            time.sleep(21)  # Пауза в 21 секунд

    gTick_size = float(get_json2.json()["symbols"][0]["filters"][0]["tickSize"])
    gDights = get_gDights(gTick_size)
    gLastPrice = round(float(result01['close']), gDights)

    # symbol_data = {}
    # symbol_data['gLastPrice'] = gLastPrice
    # symbol_data['gDights'] = gDights
    # symbol_data['gTick_size'] = gTick_size

    return gLastPrice, gDights, gTick_size

