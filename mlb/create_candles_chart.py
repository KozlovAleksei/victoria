import pandas as pd
import numpy as np
import datetime
import os
import time
from IPython.display import display
from PIL import Image


def create_candles_chart(symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl):
    print("create_candles_chart:", symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl)
    strAccountBalanceFix = str(int(gAccountBalance))
    file_path = f"{gNetRoot}orders\\{gNetCode}.txt"
    if not os.path.exists(file_path):
        print('create_candles_chart: Нет файла сетки = ', file_path)
        return None, None

    limit = 300
    r = cl.klines(symbol, interval, limit=limit)  # from binance.spot import Spot
    df = pd.DataFrame(r).iloc[:, :6]  # Use only the first 6 OHLCV columns
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']

    df['time'] = pd.to_datetime(df['time'], unit='ms')  # Assuming 'time' is represented in milliseconds
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    df.set_index('time', inplace=True)  # Set 'time' column as the index

    path = gNetRoot + "Chart\\" + datetime.datetime.now().strftime("%Y-%m-%d") + "\\"
    if not os.path.exists(path):
        os.makedirs(path)

    from bokeh.plotting import figure, output_file, save
    from bokeh.io import export_png
    from bokeh.models import LinearAxis, Range1d
    from bokeh.models import Title, Row

    # # Создание графика
    # p = figure(x_axis_type='datetime', title='Candlestick Chart', width=1280, height=1024, output_backend="svg")

    # Создание фигуры
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%d.%m.%Y %H:%M:%S')
    p = figure(x_axis_type='datetime', title='Сделки Козлова Алексея Викторовича на Binance на ' + formatted_datetime, width=1280, height=1024, output_backend="svg")

    p.grid.grid_line_alpha = 0.3

    # Определение размеров свечей
    candle_width = 60 * 1000  # 1 минута в миллисекундах

    # Отрисовка свечей
    p.segment(df.index, df.high, df.index, df.low, color='black')
    p.vbar(df.index[df.close > df.open], candle_width, df.open[df.close > df.open], df.close[df.close > df.open],
           fill_color='green', line_color='green')
    p.vbar(df.index[df.close < df.open], candle_width, df.open[df.close < df.open], df.close[df.close < df.open],
           fill_color='red', line_color='red')

    # p.segment(df.index, df.high, df.index, df.low, color='black')
    # p.rect(df.index[df.close > df.open], (df.open[df.close > df.open] + df.close[df.close > df.open]) / 2, candle_width,
    #        abs(df.open[df.close > df.open] - df.close[df.close > df.open]),
    #        fill_color='green', line_color='black')
    # p.rect(df.index[df.close < df.open], (df.open[df.close < df.open] + df.close[df.close < df.open]) / 2, candle_width,
    #        abs(df.open[df.close < df.open] - df.close[df.close < df.open]),
    #        fill_color='red', line_color='black')


    # Третья строка
    Row3 = ''
    json_data = cl.account()
    btc_balance = None
    usdt_balance = None
    for balance in json_data['balances']:
        if balance['asset'] == 'BTC':
            btc_balance = float(balance['free']) + float(balance['locked'])
        elif balance['asset'] == 'USDT':
            usdt_balance = float(balance['free']) + float(balance['locked'])

    strAccountBalanceFloat = ''
    b = ''
    u = ''
    if btc_balance != None and usdt_balance != None and gLastPrice != None:
        b = str(round(btc_balance, 6))
        k = str(round(gLastPrice, 8))
        u = str(round(usdt_balance, 2))
        strAccountBalanceFloat = str(int(btc_balance * gLastPrice + usdt_balance))
        rb = str(round(usdt_balance / gLastPrice, 6))
        Row3 = f'BTC {b} * курс= {k} + USD {u} = {strAccountBalanceFloat} ~ {rb}'

    # Вторая строка
    # Row2 = str(gSignal) + ' (' + str(gOpenLevel) + '~' + str(gCloseLevel) + ')'
    Row2 = 'btc_balance=' + b + ' ~ usdt_balance=' + u

    # Первая строка
    Row1 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ' ' + gNetCode + ' = ' + \
           strAccountBalanceFix + ' ~ ' + strAccountBalanceFloat

    # print('strAccountBalanceFloat=', strAccountBalanceFloat)

    # breakpoint()

    # Третья строка
    Row4 = ''
    if gOpenBN is not None and gOpenBN != '':
        ProfitBN = int(gAccountBalance) - int(gOpenBN)
        Row4 = 'gOpenBN= ' + gOpenBN + ' ProfitBN: ' + str(ProfitBN)

    # Добавление заголовков
    title1 = Title(text=Row1, align='center', text_font_size='11pt', text_font_style='bold')
    title2 = Title(text=Row2, align='center', text_font_size='11pt', text_font_style='bold')
    title3 = Title(text=Row3, align='center', text_font_size='11pt', text_font_style='bold')
    title4 = Title(text=Row4, align='center', text_font_size='11pt', text_font_style='bold')
    p.add_layout(title4, 'above')
    p.add_layout(title3, 'above')
    p.add_layout(title2, 'above')
    p.add_layout(title1, 'above')

    # Удаление оси цен слева
    p.yaxis.visible = False

    try:
        data = pd.read_csv(file_path, sep='\s+', usecols=['price', 'clientOrderId', 'status'])
    except ValueError:
        print("create_candles_chart: Некорректное количество имен в заголовке файла.")
        return None, None
    except Exception as e:
        print("create_candles_chart: Произошла ошибка при чтении файла ордеров:", str(e))
        return None, None

    # Extract the last character from clientOrderId
    last_character = data['clientOrderId'].str[-1]

    # Filter rows where the last character is '1' and the status is 'NEW'
    green_lines1 = data.loc[(last_character == '1') & (data['status'] == 'NEW'), 'price'].values.astype(float)
    # print(green_lines1)

    # Filter rows where the last character is '3' and the status is 'NEW'
    red_lines3 = data.loc[(last_character == '3') & (data['status'] == 'NEW'), 'price'].values.astype(float)
    # print(red_lines3)

    # Filter rows where the last character is '2' and the status is 'NEW'
    red_lines2 = data.loc[(last_character == '2') & (data['status'] == 'NEW'), 'price'].values.astype(float)
    # print(red_lines2)

    # Filter rows where the last character is '4' and the status is 'NEW'
    green_lines4 = data.loc[(last_character == '4') & (data['status'] == 'NEW'), 'price'].values.astype(float)
    # print(green_lines4)

    # Объединение всех массивов в один общий массив
    all_prices = np.concatenate((green_lines1, red_lines3, red_lines2, green_lines4))

    # print(all_prices)
    if any(all_prices):
        # Определение минимального и максимального значения из массива цен
        min_price = min(all_prices)
        max_price = max(all_prices)

        # Определение минимального и максимального значения из диапазона цен свечей
        min_candle_price = df['low'].min()
        max_candle_price = df['high'].max()

        # Учет диапазона цен свечей при определении минимального и максимального значения
        min_price = min(min_price, min_candle_price)
        max_price = max(max_price, max_candle_price)
    else:
        # Определение минимального и максимального значения из диапазона цен свечей
        min_price = df['low'].min()
        max_price = df['high'].max()

    # Создание оси цен справа
    price_range = Range1d(start=min_price, end=max_price)  # Определение диапазона цен
    # price_axis = LinearAxis(y_range_name='default', axis_label_standoff=10,
    #                         axis_label='Price', axis_label_text_font_size='30pt'
    #                         )

    price_axis = LinearAxis(y_range_name='default', axis_label_standoff=10,
                            # axis_label='Price', axis_label_text_font_size='30pt',
                            # axis_label_text_font_style='bold', axis_label_text_color='blue',
                            major_label_text_font_size='14pt', major_label_text_color='green'
                            )

    p.add_layout(price_axis, 'right')

    # Настройка диапазона оси цен
    p.y_range = price_range

    # Получение значения закрытия последней свечи
    last_close = df['close'].iloc[-1]

    # Отрисовка горизонтальной линии
    p.line([df.index[0], df.index[-1]], [last_close, last_close], line_color='magenta', line_width=1)

    # Отрисовка текстовой метки с цифрой last_close
    # p.text(df.index[-1], last_close, text=str(last_close), text_color='magenta', text_font_size='10pt',
    #        text_baseline='middle', text_align='left')

    # p.text(df.index[-1], last_close, text=[str(gSignal)], text_color='black', text_font_size='10pt',
    #        text_baseline='middle', text_align='left')

    p.text(df.index[-1], last_close, text=[str(gSignal)], text_color='black', text_font_size='10pt',
           text_baseline='middle', text_align='left', x_offset=10)

    # Отрисовка горизонтальных линий
    dash_pattern = "dashed"

    for price in green_lines1:
        p.line([df.index[0], df.index[-1]], [price, price], line_color='green', line_width=1)

    for price in red_lines3:
        p.line([df.index[0], df.index[-1]], [price, price], line_color='red', line_width=1, line_dash="dashed")

    for price in red_lines2:
        p.line([df.index[0], df.index[-1]], [price, price], line_color='red', line_width=1)

    for price in green_lines4:
        p.line([df.index[0], df.index[-1]], [price, price], line_color='green', line_width=1, line_dash="dashed")

    # Сохранение графика в графический файл
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_png(p, filename=path + filename + '.png')


    # Открываем сохраненный файл и отображаем его на экране
    # image = Image.open(path + filename + '.png')
    # display(image)

    # Отображение изображения
    # image.show()

    # Save the chart html
    # save(p)

    return strAccountBalanceFix, strAccountBalanceFloat
