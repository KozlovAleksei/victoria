import requests
from pandas import DataFrame


def get_symbol_data(symbol, interval, client, base_url="https://api.binance.com", end_point="/api/v3/exchangeInfo"):
    """
    Получает данные символа с биржи Binance.

    Args:
        symbol (str): Символ торговой пары.
        interval (str): Интервал времени.
        client (object): Объект для выполнения запросов к Binance API.
        base_url (str, optional): Базовый URL API. По умолчанию "https://api.binance.com".
        end_point (str, optional): Конечная точка API. По умолчанию "/api/v3/exchangeInfo".

    Returns:
        None
    """
    global gLastPrice, gDights, gTick_size

    def get_close_price(symbol, interval):
        df = DataFrame(client.klines(symbol, interval, limit=1)).iloc[:, :6]
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        return df.iloc[-1]

    def get_gDights(gTick_size):
        str_gTick_size = str(gTick_size)
        decimal_part = str_gTick_size.split('.')[-1]  # Получение десятичной части
        return len(decimal_part.rstrip('0'))  # Получение количества значащих символов

    get_json2 = requests.get(f"{base_url}{end_point}?symbol={symbol}")
    gTick_size = float(get_json2.json()["symbols"][0]["filters"][0]["tickSize"])
    gDights = get_gDights(gTick_size)

    result01 = get_close_price(symbol, interval)
    gLastPrice = round(float(result01['close']), gDights)

    symbol_data.gLastPrice = gLastPrice
    symbol_data.gDights = gDights
    symbol_data.gTick_size = gTick_size

    return symbol_data