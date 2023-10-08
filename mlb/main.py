from binance.spot import Spot
from binance.error import ClientError
import mlb
import time
import datetime
import os

# test
base_url = 'https://testnet.binance.vision'  # https://youtu.be/NczNjVxwx3A?t=636
api_key = 'LDt6vLKawn1VYaAs8CTwYx6RtAiVrowVe3wu1bRerko9VZ0HAr2gL7KMMS3kM5DH'
api_secret = 'nvXZgMuLaQNlbGO8STgdzMYixrhuPEwPL641F3AXwelU9LgqRDz4iYYyoWSxZDRE'
gNetRoot = "Z:\\#TEST\\"

# mlb.create_balance_chart(gNetRoot, '43000', '43000')
# breakpoint()

gCloseLevel = 5  # уровень закрытия сетки, вовремя закрыть тоже важно 5
gOpenLevel = 6  # уровень установки сетки, чем больше, тем меньше риск. Рекомендуется 6

gStartCnt = 60  # 60
gMaxCnt = gStartCnt

symbol = "BTCUSDT"
interval = "3m"


gLast_c_value = None
gLastPrice = None
gDights = None
gTick_size = None
gPrevious_candle_close = None

gNetName = None
gNetCode = None
gNetType = None
gOpenBN = None
gStartCnt = 100  # 150
gNetStep = 500  # чем больше, тем шире сетка 300


########################################################
gTP_pips = gNetStep * 5
# протестировано 5 == (0.12% ~ -0.01) за 12 ч



########################################################







gSignal = None
gLastRnd = None

gAccountBalance = None


def main(test):
    if test:
        # test
        base_url = 'https://testnet.binance.vision'  # https://youtu.be/NczNjVxwx3A?t=636
        api_key = 'LDt6vLKawn1VYaAs8CTwYx6RtAiVrowVe3wu1bRerko9VZ0HAr2gL7KMMS3kM5DH'
        api_secret = 'nvXZgMuLaQNlbGO8STgdzMYixrhuPEwPL641F3AXwelU9LgqRDz4iYYyoWSxZDRE'
        gNetRoot = "Z:\\#TEST\\"
    else:
        # real
        base_url = 'https://api2.binance.com'  # https://binance-docs.github.io/apidocs/spot/en/#general-info
        api_key = 'dHGrsHpiGqiRHzaRTLaE7139D5xmza6lRjWzGoIBXWyk6EC4XFFs7U5kPZuOBKsk'
        api_secret = 'tk9FL33R6nqzSebqLiusdhaT3NRxVXmFD2OVCJcQr2zC1CkpSzLaWRopTxxQTMNE'
        gNetRoot = "Z:\\#REAL\\"
    mlb.MkDirs(gNetRoot)
    cl = Spot(api_key=api_key, api_secret=api_secret, base_url=base_url)
    print('base_url=', base_url)
    print('cl =', cl)
    # breakpoint()
    global gNetLot
    gLast_c_value, gDights, gTick_size = mlb.get_symbol_data(symbol, interval, cl)
    #gPrevious_candle_close = mlb.get_previous_candle_close(symbol, interval, cl)
    #mlb.show_orders(symbol, gNetCode, gNetRoot, cl)
    #gAccountBalance, btc_balance, usdt_balance, BalanceFile = mlb.AccountBalance(gNetRoot, cl)
    #mlb.plot_graph(BalanceFile)
    #mlb.create_candles_chart(symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gNetCode, gNetRoot, cl)
    #gSignal = round(mlb.get_signal(symbol, interval, cl).signal, 3)

    while True:
        print('\nНачало')
        gLastPrice, gDights, gTick_size = mlb.get_symbol_data(symbol, interval, cl)

        gSignal = round(mlb.get_signal(symbol, interval, cl).signal, 3)
        if os.path.isfile(gNetRoot + symbol + '\\gNetName.txt'):
            gNetName = mlb.read_text_from_file(gNetRoot + symbol + '\\gNetName.txt')
            gNetCode = mlb.read_text_from_file(gNetRoot + symbol + '\\gNetCode.txt')
            gNetType = mlb.read_text_from_file(gNetRoot + symbol + '\\gNetType.txt')
            gOpenBN = mlb.read_text_from_file(gNetRoot + symbol + '\\gOpenBN.txt')
            gLot = mlb.read_text_from_file(gNetRoot + symbol + '\\gLot.txt')
            P0000001 = mlb.read_text_from_file(gNetRoot + symbol + '\\gNetOrd\\P0000001.txt')
            gMaxCnt = mlb.str2int(mlb.read_text_from_file(gNetRoot + symbol + '\\gMaxCnt.txt'))
            str_cnt = f"{gMaxCnt:07d}"
            P9999999 = mlb.read_text_from_file(gNetRoot + symbol + '\\gNetOrd\\P' + str_cnt + '.txt')
            if P9999999 == '':
                gMaxCnt = gMaxCnt - 1
                mlb.write_text2file(gNetRoot + symbol + '\\gMaxCnt.txt', str(gMaxCnt))

            if gNetType == 'shrt' and gLastPrice > float(P9999999):
                mlb.net_delete(symbol, 'shrt', symbol, gNetRoot, cl)
                continue

            if gNetType == 'long' and gLastPrice < float(P9999999):
                mlb.net_delete(symbol, 'long', symbol, gNetRoot, cl)
                continue
        else:
            gNetName = None
            gNetCode = None
            gNetType = None
            gOpenBN = None
            gLot = None
            P0000001 = None
            P9999999 = None

        gAccountBalance, btc_balance, usdt_balance, BalanceFile = mlb.AccountBalance(gNetRoot, cl)
        if gAccountBalance != -1:
            gNetLot = round(gAccountBalance / 3367000, 5)  # 40404 / 3367000 = 0.012
            if gNetLot < 0.005:  # https://www.youtube.com/watch?v=fWYU8VAkqfo&t=1002s
                print('gNetLot1=', gNetLot)
                gNetLot = 0.005
                print('gNetLot2=', gNetLot)
        server_time = cl.time()['serverTime']
        Time1 = datetime.datetime.fromtimestamp(server_time / 1000).strftime('%H:%M:%S')
        Time2 = datetime.datetime.now().strftime('%H:%M:%S')
        mlb.synchronize_system_time(Time1, Time2)
        Row2 = str(gSignal) + ' (' + str(gOpenLevel) + '~' + str(gCloseLevel) + ')'
        print(Row2, 'gNetCode=', gNetCode, 'gNetName=', gNetName,
              'gNetType=', gNetType, 'gLot=', gLot, 'P0000001=', P0000001, '=>', P9999999, '(',
              Time1, Time2, ') gLastPrice=', gLastPrice, 'btc_balance=', '~', btc_balance, 'usdt_balance=', usdt_balance)

        if gLast_c_value != gLastPrice:
            print('main: Новыя цена')
            # Удаление сетки при выходе через границы
            if gNetType != None and gLastPrice != None and gSignal != None and P9999999 != None and P9999999 != '':
                # print('P9999999=', P9999999)
                if gSignal >= gOpenLevel:
                    gPrevious_candle_close = mlb.get_previous_candle_close(symbol, interval, cl)
                    if gPrevious_candle_close != None and gPrevious_candle_close > float(P9999999):
                        mlb.net_delete(symbol, 'shrt', symbol, gNetRoot, cl)
                if gSignal <= -gOpenLevel:
                    gPrevious_candle_close = mlb.get_previous_candle_close(symbol, interval, cl)
                    if gPrevious_candle_close != None and gPrevious_candle_close < float(P9999999):
                        mlb.net_delete(symbol, 'long', symbol, gNetRoot, cl)

            # Новая сетка
            gNetType = None
            if gSignal >= gCloseLevel:
                mlb.net_delete(symbol, 'long', symbol, gNetRoot, cl)
                if not os.path.isdir(gNetRoot + symbol) and gSignal >= gOpenLevel:
                    gNetName = symbol
                    gNetType = 'shrt'
                    mlb.net_make(gNetType, gStartCnt, symbol, gNetLot, gNetStep, gTP_pips, gNetRoot, interval, cl)
            if gSignal <= -gCloseLevel:
                mlb.net_delete(symbol, 'shrt', symbol, gNetRoot, cl)
                if not os.path.isdir(gNetRoot + symbol) and gSignal <= -gOpenLevel:
                    gNetName = symbol
                    gNetType = 'long'
                    mlb.net_make(gNetType, gStartCnt, symbol, gNetLot, gNetStep, gTP_pips, gNetRoot, interval, cl)

            mlb.show_orders(symbol, gNetCode, gNetRoot, cl)

            strAccountBalanceFix, strAccountBalanceFloat = mlb.create_candles_chart(symbol, interval, gOpenBN, \
                gAccountBalance, gLastPrice, gSignal, gOpenLevel, gCloseLevel, gNetCode, gNetRoot, cl)

            if not (strAccountBalanceFix is None or strAccountBalanceFloat is None):
                mlb.create_balance_chart(gNetRoot, strAccountBalanceFix, strAccountBalanceFloat)

        gLast_c_value = gLastPrice

        # breakpoint()
        mlb.net_support(gNetName, gNetCode, gNetRoot, symbol, interval, gLastPrice, gStartCnt, cl)
        # create_candles_chart(symbol, interval)
        # time.sleep(2)  # Пауза в 500 миллисекунд
