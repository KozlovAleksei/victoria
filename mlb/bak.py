# В коде имеются ошибки в части управдения df (time) Методы исправления части кода не помогают. Перепиши код полностью, как бы ты это видел со своей точки зрения.
import pandas as pd
import mplfinance as mpf
import numpy as np
import datetime
import os


def create_candles_chart(symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl):
    print("create_candles_chart:", symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl)
    file_path = f"{gNetRoot}orders\\{gNetCode}.txt"
    if not os.path.exists(file_path):
        return
    limit = 300
    r = cl.klines(symbol, interval, limit=limit)
    df = pd.DataFrame(r).iloc[:, :6]  # Use only the first 6 OHLCV columns
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']

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

        # Определите 'time' как индекс
        df.set_index('time', inplace=True)
        print(df['time'])
        # Преобразуйте столбец 'time' в тип datetime
        df['time'] = pd.to_datetime(df['time'], unit='ms')  # Предполагается, что 'time' представлено в миллисекундах

        print("Проверка 1", df.index.dtype)  # Проверка типа индекса данных
        print("Проверка 2", df['time'].dtype)  # Проверка типа столбца 'time'

        mpf.plot(df, type='candle', volume=True, title=title, addplot=addplots,
                     savefig=path + Row0 + ".png", figscale=figscale, figsize=figsize)

    else:
        print('create_candles_chart: No data available in', file_path)


