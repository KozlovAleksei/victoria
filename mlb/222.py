import pandas as pd
import numpy as np
import datetime
import os
import time
from IPython.display import display
from PIL import Image


def create_candles_chart(symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl):
    print("create_candles_chart:", symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl)
    file_path = f"{gNetRoot}orders\\{gNetCode}.txt"
    if not os.path.exists(file_path):
        return
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
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    from bokeh.plotting import figure, output_file, save
    from bokeh.io import export_png
    from bokeh.models import LinearAxis, Range1d
    from bokeh.models import Title, Row

    # Создание графика
    p = figure(x_axis_type='datetime', title='Candlestick Chart', width=1280, height=1024, output_backend="svg")

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

    # Добавление заголовков
    title1 = Title(text='Стока1', align='center', text_font_size='11pt', text_font_style='bold')
    title2 = Title(text='Стока2', align='center', text_font_size='11pt', text_font_style='bold')
    title3 = Title(text='Стока3', align='center', text_font_size='11pt', text_font_style='bold')
    p.add_layout(title1, 'above')
    p.add_layout(title2, 'above')
    p.add_layout(title3, 'above')

    # Удаление оси цен слева
    p.yaxis.visible = False

    # Массив цен
    prices = [29100, 28800]

    try:
        data = pd.read_csv(file_path, sep='\s+', usecols=['price', 'clientOrderId', 'status'])
    except ValueError:
        print("Некорректное количество имен в заголовке файла. Переставить сетку?")
        breakpoint()
        return
    except Exception as e:
        print("Произошла ошибка при чтении файла ордеров:", str(e))
        return

    # Extract the last character from clientOrderId
    last_character = data['clientOrderId'].str[-1]

    import pandas as pd

    try:
        data = pd.read_csv(file_path, sep='\s+', usecols=['price', 'clientOrderId', 'status'])
    except ValueError:
        print("Некорректное количество имен в заголовке файла. Переставить сетку?")
        breakpoint()
        return
    except Exception as e:
        print("Произошла ошибка при чтении файла ордеров:", str(e))
        return

    # Extract the last character from clientOrderId
    last_character = data['clientOrderId'].str[-1]

    # Filter rows where the last character is '1' and the status is 'NEW'
    green_lines1 = data.loc[(last_character == '1') & (data['status'] == 'NEW'), 'price'].values.astype(float)

    # Filter rows where the last character is '3' and the status is 'NEW'
    red_lines3 = data.loc[(last_character == '3') & (data['status'] == 'NEW'), 'price'].values.astype(float)

    # Filter rows where the last character is '2' and the status is 'NEW'
    red_lines2 = data.loc[(last_character == '2') & (data['status'] == 'NEW'), 'price'].values.astype(float)

    # Filter rows where the last character is '4' and the status is 'NEW'
    green_lines4 = data.loc[(last_character == '4') & (data['status'] == 'NEW'), 'price'].values.astype(float)

    # Объединение всех массивов в один общий массив
    prices = np.concatenate((green_lines1, red_lines3, red_lines2, green_lines4))

    # Определение минимального и максимального значения из общего массива цен
    min_price = np.min(prices)
    max_price = np.max(prices)

    # Определение минимального и максимального значения из диапазона цен свечей
    min_candle_price = df['low'].min()
    max_candle_price = df['high'].max()

    # Учет диапазона цен свечей при определении минимального и максимального значения
    min_price = min(min_price, min_candle_price)
    max_price = max(max_price, max_candle_price)

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

    # Отрисовка горизонтальных линий
    for price in prices:
        p.line([df.index[0], df.index[-1]], [price, price], line_color='red', line_width=1)

    # Сохранение графика в графический файл
    export_png(p, filename=path + filename + '.png')


    # Открываем сохраненный файл и отображаем его на экране
    image = Image.open(path + filename + '.png')
    display(image)

    # Отображение изображения
    # image.show()

    breakpoint()




    print('save=', path + filename)
    print(df)

    # Create the candlestick chart using mplfinance
    mpf.plot(df, type='candle', style='charles', savefig=path + filename + '.png')




    # Example usage

    breakpoint()



    if len(df) > 0:
        # Create the horizontal line addplot
        # solid dashed dotted dashdot dashdotdot

        print('gLastPrice=', float(gLastPrice))

        # Create a DataFrame with a single row containing gLastPrice
        data = pd.DataFrame({'Close': [gLastPrice]})

        print('data[Close]=', data['Close'])

        hline = mpf.make_addplot(data['Close'], color='magenta', width=0.4, linestyle='solid', secondary_y=False)

        # Create the green lines addplot
        try:
            data = pd.read_csv(file_path, sep='\s+', usecols=['price', 'clientOrderId', 'status'])
        except ValueError:
            print("Некорректное количество имен в заголовке файла. Переставить сетку?")
            breakpoint()
            return
        except Exception as e:
            print("Произошла ошибка при чтении файла ордеров:", str(e))
            return

        # Extract the last character from clientOrderId
        last_character = data['clientOrderId'].str[-1]

        # Filter rows where the last character is '1' and the status is 'FILLED'
        green_lines1 = data.loc[(last_character == '1') & (data['status'] == 'NEW'), 'price'].values.astype(float)
        red_lines3 = data.loc[(last_character == '3') & (data['status'] == 'NEW'), 'price'].values.astype(float)
        red_lines2 = data.loc[(last_character == '2') & (data['status'] == 'NEW'), 'price'].values.astype(float)
        green_lines4 = data.loc[(last_character == '4') & (data['status'] == 'NEW'), 'price'].values.astype(float)

        # Create the green lines addplot
        addplots = []
        addplots.append(hline)
        for line in green_lines1:
            line_values = np.array([line] * len(df), dtype=float)
            hline = mpf.make_addplot(line_values, color='green', width=1, secondary_y=False)
            addplots.append(hline)

        for line in red_lines3:
            line_values = np.array([line] * len(df), dtype=float)
            hline = mpf.make_addplot(line_values, color='brown', linestyle='dashdot', width=1, secondary_y=False)
            addplots.append(hline)

        for line in red_lines2:
            line_values = np.array([line] * len(df), dtype=float)
            hline = mpf.make_addplot(line_values, color='red', width=1, secondary_y=False)
            addplots.append(hline)

        for line in green_lines4:
            line_values = np.array([line] * len(df), dtype=float)
            hline = mpf.make_addplot(line_values, color='blue', linestyle='dashdot', width=1, secondary_y=False)
            addplots.append(hline)

        # Папка
        folder = datetime.datetime.now().strftime("%Y-%m-%d")

        # имя файла
        Row0 = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ' ' + gNetCode + '= ' + str(int(gAccountBalance))

        # Первая строка
        Row1 = '\n\n\n\n' + Row0 + '\n'

        # Вторая строка
        Row2 = str(gSignal) + ' (' + str(gOpenLevel) + '~' + str(gCloseLevel) + ')' + '\n'

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

        if btc_balance != None and usdt_balance != None and gLastPrice != None:
            b = str(round(btc_balance, 6))
            k = str(round(gLastPrice, 8))
            u = str(round(usdt_balance, 2))
            ru = str(int(btc_balance * gLastPrice + usdt_balance))
            rb = str(round(usdt_balance / gLastPrice, 6))
            Row3 = f'BTC {b} * курс= {k} + USD {u} = {ru} ~ {rb}'

        # Третья строка
        Row4 = ''
        if gOpenBN is not None and gOpenBN != '':
            ProfitBN = int(gAccountBalance) - int(gOpenBN)
            Row4 = '\ngOpenBN= ' + gOpenBN + ' ProfitBN: ' + str(ProfitBN)

        title = f'{Row1}{Row2}{Row3}{Row4}'

        # Параметры масштабирования и разрешения графика

        figscale = 1.0  # Увеличение масштаба графика
        figsize = (12, 15)  # Размеры графика (ширина, высота) figsize = (12, 12)

        path = gNetRoot + "Chart\\" + folder + "\\"
        if not os.path.exists(path):
            os.makedirs(path)

        df['time'] = pd.to_datetime(df['time'], unit='ms')  # Предполагается, что 'time' представлено в миллисекундах
        time.sleep(3)
        # Определите 'time' как индекс
        df.set_index('time', inplace=True)
        time.sleep(3)
        print(df)
        print("Проверка 1", df.index.dtype)  # Проверка типа индекса данных == Проверка 2 datetime64[ns]
        # Преобразование столбцов в числовой формат
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        time.sleep(3)
        # import mplfinance as mpf

        addplots = [{'data': df['close'], 'type': 'line', 'color': 'magenta', 'linewidth': 2}]

        print('addplots=', addplots)

        mpf.plot(df, type='candle', volume=True, title=title, addplot=addplots,
                 savefig=path + Row0 + ".png", figscale=figscale, figsize=figsize)

    else:
        print('create_candles_chart: No data available in', file_path)
