# https://binance-docs.github.io/apidocs/spot/en/#new-order-trade
# https://python-binance.readthedocs.io/en/latest/overview.html
#import win32api
import subprocess
import requests
#import logging
from binance.spot import Spot
from binance.error import ClientError
import mplfinance as mpf
import pandas as pd
import numpy as np
import datetime
from pandas import DataFrame
import random
import time
import os
import shutil
import json
import string
import mlb

import matplotlib  # pip install matplotlib
matplotlib.use('TkAgg')  # Используем интерактивную среду TkAgg
import matplotlib.pyplot as plt

#breakpoint()
end_point = "/api/v3/exchangeInfo"
## real
base_url = 'https://api2.binance.com'  # https://binance-docs.github.io/apidocs/spot/en/#general-info
api_key = 'dHGrsHpiGqiRHzaRTLaE7139D5xmza6lRjWzGoIBXWyk6EC4XFFs7U5kPZuOBKsk'
api_secret = 'tk9FL33R6nqzSebqLiusdhaT3NRxVXmFD2OVCJcQr2zC1CkpSzLaWRopTxxQTMNE'

# test
base_url = 'https://testnet.binance.vision'  # https://youtu.be/NczNjVxwx3A?t=636
api_key = 'LDt6vLKawn1VYaAs8CTwYx6RtAiVrowVe3wu1bRerko9VZ0HAr2gL7KMMS3kM5DH'
api_secret = 'nvXZgMuLaQNlbGO8STgdzMYixrhuPEwPL641F3AXwelU9LgqRDz4iYYyoWSxZDRE'

global gLastPrice
global gDights
global gTick_size


symbol = "BTCUSDT"
interval = "1m"
gNetRoot = "Z:\\#NET\\"
print(gNetRoot)

cl = Spot(api_key=api_key, api_secret=api_secret, base_url=base_url)  # Ctrl+Left_Click по Spot

TimeCurrent = cl.time()['serverTime']
print(TimeCurrent, '~', pd.to_datetime(TimeCurrent, unit='ms'))
#print(cl.klines("BTCUSDT", "1m"))
print(" ")
print(cl.account())
print(" ")
print(cl.my_trades(symbol))
#
# print(cl.get_order(symbol, origClientOrderId='FFFFGGHH'))
#
# breakpoint()
gCloseLevel = 5  # уровень закрытия сетки, вовремя закрыть тоже важно 5
gOpenLevel = 6  # уровень установки сетки, чем больше, тем меньше риск. Рекомендуется 6

# btc_balance = None
# usdt_balance = None

gStartCnt = 60  # 60
gMaxCnt = gStartCnt

gTail = gMaxCnt + 1

gNetStep = 300  # чем больше, тем шире сетка 300
gTP_pips = gNetStep * 5

gLot = None
gNetLot = 0.012  # чем меньше, тем шире сетка (отсечка по депозиту отрезает лишние файлы)
# -2010 Account has insufficient balance for requested action.
# -1105 Parameter 'quantity' was empty.

gNetName = None
gNetCode = None
gNetType = None
gOpenBN = None

gSignal = None
gLastRnd = None

gTick_size = None
gDights = None
gLastPrice = -1  # Expected type 'float', got 'None' instead : run gLastPrice: None = None

gAccountBalance = None
gReBalance = False

gBalance_tuple = {}



gNetFolder = None
gNetOrd = None

# https://binance-docs.github.io/apidocs/spot/en/#exchange-information

#r = requests.get(f"{base_url}{end_point}?symbol=BTCUSDT")
#print(r.text)

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

gLast_c_value = None

def write_text2file(filename_w, text_w):
    for t in range(1, 20000):
        time.sleep(0.001)
        with open(filename_w, 'w') as file_handle:
            file_handle.write(str(text_w))
            return

def read_text_from_file(TextFileName):
    try:
        with open(TextFileName, "r") as file:
            text = file.read()
            return text
    except FileNotFoundError:
        return ''

def format_timestamp(timestamp):
    microseconds = (timestamp % 1000) * 1000
    datetime_obj = datetime.datetime.fromtimestamp(timestamp // 1000).replace(microsecond=microseconds)
    formatted_datetime = datetime_obj.strftime('%d.%m.%Y %H:%M:%S')
    return formatted_datetime


def get_macd(symbol, interval):
    time.sleep(1)  # Пауза в 500 миллисекунд
    limit = 298  # лимит для вычисления сигнала
    r = cl.klines(symbol, interval, limit=limit)
    df = DataFrame(r).iloc[:, :7]
    df.columns = list("bohlcve")
    df['b'] = df['b'].apply(format_timestamp)
    df['e'] = df['e'].apply(format_timestamp)
    df['ma_fast'] = df['c'].ewm(span=12, adjust=False).mean()
    df['ma_slow'] = df['c'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    return df.iloc[-1]


def get_str_rnd(cnt):
    global gLastRnd

    if cnt is None:
        cnt = 8

    while True:
        characters = string.digits + string.ascii_letters  # Цифры и латинские буквы
        RetCode = ''.join(random.choice(characters) for _ in range(cnt))

        if RetCode != gLastRnd:
            gLastRnd = RetCode
            return RetCode
        time.sleep(0.001)

def get_gDights(gTick_size):
    str_gTick_size = str(gTick_size)
    decimal_part = str_gTick_size.split('.')[-1]  # Получение десятичной части
    return len(decimal_part.rstrip('0'))  # Получение количества значащих символов


def net_make(gNetType, gMaxCnt, symbol, gLot, gLastPrice, gNetStep, gTP_pips):
    global gNetRoot, gNetName, gNetFolder, gNetCode
    #symbol = get_open_symbol()
    gNetCode = gNetType[0]+get_str_rnd(4)
    print('net_make:', gNetName, gNetCode, gNetType, gMaxCnt, symbol, gLot, gLastPrice, gNetStep, gTP_pips)
    if not isinstance(gNetName, str):
        breakpoint()
        return
    gNetFolder = gNetRoot + gNetName + '\\'
    gNetOrd = gNetFolder + 'gNetOrd\\'
    if not os.path.exists(gNetFolder):
        os.makedirs(gNetFolder)
        os.makedirs(gNetOrd)
    else:
        return
    # account()
    print(gNetFolder)
    write_text2file(gNetFolder + 'gNetName.txt', gNetName)
    write_text2file(gNetFolder + 'gNetCode.txt', gNetCode)
    write_text2file(gNetFolder + 'gNetType.txt', gNetType)
    write_text2file(gNetFolder + 'gMaxCnt.txt', str(gMaxCnt))
    write_text2file(gNetFolder + 'symbol.txt', symbol)
    write_text2file(gNetFolder + 'gLot.txt', str(gLot))
    write_text2file(gNetFolder + 'gLastPrice.txt', str(gLastPrice))
    write_text2file(gNetFolder + 'gNetStep.txt', str(gNetStep))
    write_text2file(gNetFolder + 'gTP_pips.txt', str(gTP_pips))
    price_up = gLastPrice
    price_dn = gLastPrice
    SL_pice = None

    for cnt in range(1, gMaxCnt + 1):
        str_cnt = f"{cnt:07d}"
        write_text2file(gNetOrd + 'T' + str_cnt + '.txt', gNetCode+get_str_rnd(4))
        price_dn = round(float(price_dn), gDights)
        price_up = round(float(price_up), gDights)

        if gNetType == 'long':
            price_dn = round(price_dn - (gTick_size * gNetStep), gDights)
            write_text2file(gNetOrd + 'P' + str_cnt + '.txt', price_dn)
            write_text2file(gNetOrd + 'F' + str_cnt + '.txt', round(price_dn + (gTick_size * gTP_pips), gDights))
            SL_pice = round(price_dn - (gTick_size * gTP_pips), gDights)

        if gNetType == 'shrt':
            price_up = round(price_up + (gTick_size * gNetStep), gDights)
            write_text2file(gNetOrd + 'P' + str_cnt + '.txt', price_up)
            write_text2file(gNetOrd + 'F' + str_cnt + '.txt', round(price_up - (gTick_size * gTP_pips), gDights))
            SL_pice = round(price_up + (gTick_size * gTP_pips), gDights)

    write_text2file(gNetFolder + 'gSL_L.txt', SL_pice)
    write_text2file(gNetFolder + 'gSL_T.txt', gNetCode+get_str_rnd(4))
    ReBalanceAccount(symbol)  # При создании сетки
    write_text2file(gNetFolder + 'gOpenBN.txt', str(int(AccountBalance())))
    # breakpoint()
    return

def is_order_by_T(symbol, T):
    try:
        cl.get_order(symbol, origClientOrderId=T)
        return True
    except ClientError:
        return False

def get_status_buy_order_by_T(symbol, T):
    try:
        order = cl.get_order(symbol, origClientOrderId=T)
        if order["side"] == "BUY":
            return order["status"]
        return 'EMPTY'
    except ClientError:
        return 'EMPTY'


def get_status_sell_order_by_T(symbol, T):
    try:
        order = cl.get_order(symbol, origClientOrderId=T)
        if order["side"] == "SELL":
            return order["status"]
        return 'EMPTY'
    except ClientError:
        return 'EMPTY'


def send_limit_order(symbol, side, gLot, P, T, prichina):
    if P == '':
        print(prichina, 'send_limit_order: P=', P)
        return -1
    P = round(float(P), gDights)
    gLot = float(gLot)  # Convert gLot to float
    gLot = "{:.6f}".format(gLot)  # убираем 9e-05
    deals('send_limit_order', symbol, gLot, str(P), T, side)
    try:
        result = cl.new_order(
            newClientOrderId=T,
            symbol=symbol,
            side=side,
            type='LIMIT',
            price=P,
            quantity=gLot,
            timeInForce='GTC'
        )
        #print(result)
        return 0
    except ClientError as e:
        print(e.error_code, e.error_message)
        # if e.error_code == -2010:
        #     ReBalanceAccount(symbol)  # В случае недостатка средств при создании лимитки
        return e.error_code  # -2010 Account has insufficient balance for requested action.


def send_market_order(symbol, side, gLot, P, T):
    gLot = float(gLot)  # Convert gLot to float
    gLot = "{:.6f}".format(gLot)  # убираем 9e-05
    deals('send_market_order', symbol, gLot, P, T, side)
    try:
        result = cl.new_order(
            newClientOrderId=T,
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=gLot,
        )
        print(result)
        return 0
    except ClientError as e:
        print(e.error_code, e.error_message)
        return e.error_code  # -2010 Account has insufficient balance for requested action.


def int0(str):
    try:
        return int(str)
    except ValueError:
        return -1

def set_gMaxCnt():
    gNetFolder = gNetRoot + gNetName + '\\'
    gNetOrd = gNetFolder + 'gNetOrd\\'
    fileCount = 0
    for _, _, files in os.walk(gNetOrd):
        for file in files:
            if file != "." and file != "..":
                fileCount += 1
    gMaxCnt = fileCount // 3
    write_text2file(gNetFolder + 'gMaxCnt.txt', str(gMaxCnt))

def net_support(gNetName):
    global gReBalance
    gReBalance = True
    gNetFolder = gNetRoot + gNetName + '\\'
    gNetOrd = gNetFolder + 'gNetOrd\\'
    gMaxCnt = int0(read_text_from_file(gNetFolder + 'gMaxCnt.txt'))

    for cnt in range(1, gMaxCnt + 1):
        str_cnt = f"{cnt:07d}"
        T = read_text_from_file(gNetOrd + 'T' + str_cnt + '.txt')
        gNetType = read_text_from_file(gNetFolder + 'gNetType.txt')

        # выставляем ордера, если не выставлены.
        if gNetType == 'long' and not is_order_by_T(symbol, f"{T}1"):
            gLot = read_text_from_file(gNetFolder + 'gLot.txt')
            P = read_text_from_file(gNetOrd + 'P' + str_cnt + '.txt')
            RetCode = send_limit_order(symbol, 'BUY', gLot, P, f"{T}1", f"New long P{str_cnt}.txt={P}")
            if RetCode == -1:
                set_gMaxCnt()
                return
            if RetCode == -2010 and gMaxCnt == gStartCnt and gReBalance:  # Account has insufficient balance for requested action.
                gReBalance = False
                print('Урезаю long массив до', cnt)
                for cnt2 in range(cnt, gStartCnt + 1):
                    print('cnt2=', cnt2)
                    if cnt2 > 10:
                        str_cnt2 = f"{cnt2:07d}"
                        T2 = read_text_from_file(gNetOrd + 'T' + str_cnt2 + '.txt')
                        print('len(T2)=', len(T2), ' ~ ', T2)
                        if len(T2) == 9 and not is_order_by_T(symbol, f"{T2}1"):
                            print('Удаляю избыточные файлы long ' + str_cnt2)
                            os.remove(gNetOrd + 'T' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'P' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'F' + str_cnt2 + '.txt')
                set_gMaxCnt()
                return
            # if RetCode == -2010:
            #     gReBalance = True

        if gNetType == 'shrt' and not is_order_by_T(symbol, f"{T}2"):
            gLot = read_text_from_file(gNetFolder + 'gLot.txt')
            P = read_text_from_file(gNetOrd + 'P' + str_cnt + '.txt')
            RetCode = send_limit_order(symbol, 'SELL', gLot, P, f"{T}2", f"New shrt P{str_cnt}.txt={P}")
            if RetCode == -1:
                set_gMaxCnt()
                return
            if RetCode == -2010 and gMaxCnt == gStartCnt and gReBalance:  # Account has insufficient balance for requested action.
                gReBalance = False
                print('Урезаю shrt массив до', cnt)
                for cnt2 in range(cnt, gStartCnt + 1):
                    print('cnt2=', cnt2)
                    if cnt2 > 10:
                        str_cnt2 = f"{cnt2:07d}"
                        T2 = read_text_from_file(gNetOrd + 'T' + str_cnt2 + '.txt')
                        print('len(T2)=', len(T2), ' ~ ', T2)
                        if len(T2) == 9 and not is_order_by_T(symbol, f"{T2}2"):
                            print('Удаляю избыточные файлы shrt ' + str_cnt2)
                            os.remove(gNetOrd + 'T' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'P' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'F' + str_cnt2 + '.txt')
                set_gMaxCnt()
                return

        # чекаем ордера и выставляем TP, если его нет.
        if gNetType == 'long' and not is_order_by_T(symbol, f"{T}3") \
            and get_status_buy_order_by_T(symbol, f"{T}1") == 'FILLED':
                gLot = read_text_from_file(gNetFolder + 'gLot.txt')
                F = read_text_from_file(gNetOrd + 'F' + str_cnt + '.txt')
                send_limit_order(symbol, 'SELL', gLot, F, f"{T}3", f"TP for long F{str_cnt}.txt={F}")

        if gNetType == 'shrt' and not is_order_by_T(symbol, f"{T}4") \
            and get_status_sell_order_by_T(symbol, f"{T}2") == 'FILLED':
                gLot = read_text_from_file(gNetFolder + 'gLot.txt')
                F = read_text_from_file(gNetOrd + 'F' + str_cnt + '.txt')
                send_limit_order(symbol, 'BUY', gLot, F, f"{T}4", f"TP for shrt F{str_cnt}.txt={F}")

            # чекаем TP, если исполнен, то делаем новый trans_id
        if gNetType == 'long' and get_status_sell_order_by_T(symbol, f"{T}3") == 'FILLED':
            filename = gNetOrd + 'T' + str_cnt + '.txt'
            while os.path.isfile(filename):
                os.remove(filename)
            new_T = gNetCode+get_str_rnd(4)
            write_text2file(filename, new_T)
            check_T = read_text_from_file(filename)
            while check_T != new_T:
                write_text2file(filename, new_T)
                check_T = read_text_from_file(filename)

        if gNetType == 'shrt' and get_status_buy_order_by_T(symbol, f"{T}4") == 'FILLED':
            filename = gNetOrd + 'T' + str_cnt + '.txt'
            new_T = gNetCode+get_str_rnd(4)
            write_text2file(filename, new_T)
            check_T = read_text_from_file(filename)
            while check_T != new_T:
                write_text2file(filename, new_T)
                check_T = read_text_from_file(filename)
    return

def close_un_pair(symbol):
    print('close_un_pair', symbol)
    # gNetFolder = gNetRoot + gNetName + '\\'
    # gNetOrd = gNetFolder + 'gNetOrd\\'
    # gMaxCnt = int0(read_text_from_file(gNetFolder + 'gMaxCnt.txt'))
    #
    # for cnt in range(1, gMaxCnt + 1):
    #     str_cnt = f"{cnt:07d}"
    #     T = read_text_from_file(gNetOrd + 'T' + str_cnt + '.txt')
    #
    #     # закрываем TP-ордер, если у него нет пары
    #     if get_status_buy_order_by_T(symbol, f"{T}1") == 'FILLED' and get_status_sell_order_by_T(symbol, f"{T}3") != 'FILLED':
    #         bidPrice = float(cl.book_ticker(symbol=symbol).get('bidPrice'))
    #         send_limit_order(symbol, 'SELL', gLot, bidPrice-(gTick_size * 30), f"{T}3")
    #     if get_status_sell_order_by_T(symbol, f"{T}2") == 'FILLED' and get_status_buy_order_by_T(symbol, f"{T}4") != 'FILLED':
    #         askPrice = float(cl.book_ticker(symbol=symbol).get('askPrice'))
    #         print(symbol, 'BUY', gLot, askPrice+(gTick_size * 30), f"{T}4")
    #         send_limit_order(symbol, 'BUY', gLot, askPrice+(gTick_size * 30), f"{T}4")

def delete_all_orders(symbol):
    print('delete_all_orders', symbol)
    # gNetFolder = gNetRoot + gNetName + '\\'
    # gNetOrd = gNetFolder + 'gNetOrd\\'
    # gMaxCnt = int0(read_text_from_file(gNetFolder + 'gMaxCnt.txt'))
    # for cnt in range(1, gMaxCnt + 1):
    #     str_cnt = f"{cnt:07d}"
    #     T = read_text_from_file(gNetOrd + 'T' + str_cnt + '.txt')
    #     try:
    #         cl.cancel_order(symbol=symbol, origClientOrderId=f"{T}4")
    #     except ClientError:
    #         pass
    #     try:
    #         cl.cancel_order(symbol=symbol, origClientOrderId=f"{T}3")
    #     except ClientError:
    #         pass
    #     try:
    #         cl.cancel_order(symbol=symbol, origClientOrderId=f"{T}2")
    #     except ClientError:
    #         pass
    #     try:
    #         cl.cancel_order(symbol=symbol, origClientOrderId=f"{T}1")
    #     except ClientError:
    #         pass
    try:
        cl.cancel_open_orders(symbol, recvWindow=59000)
    except ClientError:
        pass

def net_delete(gNetName, gNetType, symbol, gBalance_tuple):
    gNetFolder = gNetRoot + gNetName + '\\'
    if read_text_from_file(gNetFolder + 'gNetType.txt') != gNetType:  # отбрасываем сетку с ненужным направлением
        return
    if not os.path.isdir(gNetRoot + gNetName):  # если нет папки сетки, то возврат
        return
    print('net_delete:', gNetName, gNetType, read_text_from_file(gNetFolder + 'gNetCode.txt'))
    for _ in range(2):  # повторить 2 раза
        delete_all_orders(symbol)
        close_un_pair(symbol)
        time.sleep(6)  # Пауза в 6 сек
    #ReBalanceAccount(symbol)
    #account()
    #AccountBalance()
    # file_list = os.listdir(gNetFolder)
    # for file_name in file_list:
    #     os.remove(os.path.join(gNetFolder, file_name))

    shutil.rmtree(gNetRoot + gNetName)  # удаляем папку сети
    while os.path.isdir(gNetRoot + gNetName):
        print('Не смог удалить папку', gNetRoot + gNetName)
        shutil.rmtree(gNetRoot + gNetName)  # удаляем папку сети
        time.sleep(5)  # Пауза в 500 миллисекунд

    #gBalance_tuple = update_balance_file(cl.account(), gBalance_tuple)
    return gBalance_tuple


def deals(g1, g2, g3, g4, g5, g6):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    line = f'{timestamp}\t{g1}\t{g2}\t{g3}\t{g4}\t{g5}\t{g6}\n'
    print(line)
    return
    filename = gNetRoot + 'Deals.xls'
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(line)


def AccountBalance():
    btc_balance = None
    usdt_balance = None

    json_data = cl.account()
    for balance in json_data['balances']:
        if balance['asset'] == 'BTC':
            btc_balance = float(balance['free']) + float(balance['locked'])
        elif balance['asset'] == 'USDT':
            usdt_balance = float(balance['free']) + float(balance['locked'])

    # sellPrice = float(cl.book_ticker(symbol='BTCUSDT').get('bidPrice'))
    sellPrice = 30000  # Устанавливаем фиксированную, иначе не понятно растут деньги или нет

    if btc_balance is not None and usdt_balance is not None and sellPrice is not None:
        # Расчет итоговой суммы в USDT
        gAccountBalance = float((btc_balance * sellPrice) + usdt_balance)
        print('btc_balance=', round(btc_balance, 5),
              '~', int(gAccountBalance-usdt_balance),
              'usdt_balance=', int(usdt_balance),
               'AccountBalance=', int(gAccountBalance))

        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        line = f'{timestamp}\t{int(gAccountBalance)}\n'

        filename = gNetRoot + datetime.datetime.now().strftime('%d-%m-%Y') + ' (' + str(gOpenLevel) + '~' + str(gCloseLevel) + ')' + '.txt'
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(line)
            plot_graph(filename)
        return gAccountBalance

    return -1


def ReBalanceAccount(symbol):
    global gLastPrice, gNetCode
    if gLastPrice == None or gNetCode == None:
        return
    btc_balance = None
    usdt_balance = None
    print('ReBalanceAccount')
    get_symbol_data(symbol)
    json_data = cl.account()
    for balance in json_data['balances']:
        if balance['asset'] == 'BTC':
            btc_balance = float(balance['free']) + float(balance['locked'])
        elif balance['asset'] == 'USDT':
            usdt_balance = float(balance['free']) + float(balance['locked'])
    get_symbol_data(symbol)
    print('btc_balance', btc_balance)
    print('usdt_balance', usdt_balance)
    print('gLastPrice', gLastPrice)
    if btc_balance is not None and usdt_balance is not None:
        filename = gNetRoot + "orders\\" + gNetCode + "_RB.txt"

        print('ReBalanceAccount: gLastPrice=', gLastPrice)
        BTC_in_USDT=btc_balance * gLastPrice  # Количество BTC в долларах
        if BTC_in_USDT > usdt_balance: #  Продать BTC
            sell_summ_usd = (BTC_in_USDT - usdt_balance) / 2
            BTC_to_sell = sell_summ_usd / gLastPrice
            if BTC_to_sell >= 0.001:
                try:
                    send_market_order(symbol, 'SELL', round(BTC_to_sell, 6), 'Market', 'ReBalance')
                    write_text2file(filename, 'SELL Market BTC at price=' + str(gLastPrice) + 'QTY=' + str(BTC_to_sell))
                except Exception as e:
                    print("Произошла ошибка при SELL-ReBalance:", e)

        if BTC_in_USDT < usdt_balance: #  Купить BTC
            buy_summ_usd = (usdt_balance - BTC_in_USDT) / 2
            BTC_to_buy = round(buy_summ_usd / gLastPrice, 6)
            if BTC_to_buy >= 0.001:
                try:
                    send_market_order(symbol, 'BUY', BTC_to_buy, 'Market', 'ReBalance')
                    write_text2file(filename, 'BUY Market BTC at price=' + str(gLastPrice) + 'QTY=' + str(BTC_to_buy))
                except Exception as e:
                    print("Произошла ошибка при BUY-ReBalance:", e)
    return


def account():
    json_data = cl.account()
    filtered_data = [item for item in json_data['balances'] if item['asset'] in ['BTC', 'USDT']]
    formatted_data = json.dumps(filtered_data, indent=4)
    print(formatted_data)


def get_open_symbol():
    # сначала получаем массив валют из "asset": "BTC" и т.п.
    json_data = cl.account()
    valuta = []
    for balance in json_data['balances']:
        asset = balance['asset']
        valuta.append(asset)
    # имеем массив валют,  необходимо создать массив всех возможных парных комбинаций между ними
    # Создаем массив всех возможных парных комбинаций
    pairs = []
    bases = []
    quotes = []
    signal = []

    for i in range(len(valuta)):
        for j in range(i + 1, len(valuta)):
            pair = valuta[i] + valuta[j]
            base = valuta[i]
            quote = valuta[j]
            try:
                s = get_macd(pair, interval='1m').signal
                pairs.append(pair)
                bases.append(base)
                quotes.append(quote)
                signal.append(s)
            except:
                pass

    # Сортируем пары и сигналы по убыванию сигнала
    sorted_pairs_signal = sorted(zip(pairs, bases, quotes, signal), key=lambda x: x[3], reverse=True)

    max_signal = float('-inf')  # Инициализируем максимальный сигнал как минус бесконечность
    max_pair = None  # Инициализируем максимальную пару как пустое значение

    # Выводим отсортированные пары и сигналы на экран
    for pair, base, quote, s in sorted_pairs_signal:
        print(f"Pair: {pair}, base: {base}, quote: {quote}, Signal: {s}")

        if s > max_signal:  # Если текущий сигнал больше максимального
            max_signal = s  # Обновляем максимальный сигнал
            max_pair = (pair, base, quote)  # Обновляем максимальную пару

    print("Максимальная пара:")
    print(f"Pair: {max_pair[0]}, base: {max_pair[1]}, quote: {max_pair[2]}, Signal: {max_signal}")
    print(max_pair[0])
    return max_pair[0]  # нужны консолидации, а они на пиках


def update_balance_file(balance_json, gBalance_tuple, separator=None):
    return
    balances = balance_json['balances']
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')

    # Преобразование числовых значений в строки с запятой в качестве разделителя десятичных чисел
    formatted_balances = [balance['free'].replace('.', ',') for balance in balances]
    formatted_balances.insert(0, gLastPrice)
    formatted_balances.insert(0, timestamp)

    if gBalance_tuple == tuple(formatted_balances[2:]):
        return gBalance_tuple

    filename = gNetRoot + datetime.datetime.now().strftime('%d-%m-%Y') + '.txt'

    with open(filename, 'a' if separator is None else 'at', encoding='utf-8') as file:
        if separator is None:
            file.write('\t'.join(formatted_balances) + '\n')
        else:
            file.write(separator.join(formatted_balances) + '\n')

    return tuple(formatted_balances[2:])  # Возвращаем балансы без временной метки


def synchronize_system_time(time1, time2):
    # Внимание - надо включить галочку устанавливать время автоматически, иначе не синхронизируется
    if time1 != time2:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        time_difference = datetime.datetime.strptime(time1, "%H:%M:%S") - datetime.datetime.strptime(time2, "%H:%M:%S")

        # Определяем, в какую сторону нужно сдвинуть время
        if time_difference.total_seconds() < 0:
            time_shift = "+" + str(abs(time_difference.seconds))
        else:
            time_shift = "-" + str(abs(time_difference.seconds))

        # Вызываем команду для синхронизации времени в Windows
        subprocess.run(
            ["w32tm", "/resync", "/force", "/manualpeerlist:time.windows.com", "/syncfromflags:manual", "/update",
             "/adjustphase:" + time_shift])

        # Проверяем, что системное время успешно синхронизировано
        updated_time = datetime.datetime.now().strftime("%H:%M:%S")
        if updated_time == current_time:
            print("Системное время успешно синхронизировано!")
        else:
            print("Не удалось синхронизировать системное время.")

def Get_Symbol_Info(symbol):
    result01 = get_macd(symbol, interval)
    get_json2 = requests.get(f"{base_url}{end_point}?symbol={symbol}")
    gTick_size = float(get_json2.json()["symbols"][0]["filters"][0]["tickSize"])
    gDights = get_gDights(gTick_size)

    Get_Symbol_Info.gLastPrice = round(float(result01.c), gDights)
    Get_Symbol_Info.gDights = gDights
    Get_Symbol_Info.gTick_size = gTick_size
    return Get_Symbol_Info


def plot_graph(file_path):
    # Считываем данные из файла
    times = []
    values = []
    with open(file_path, 'r') as file:
        for line in file:
            time, value = line.strip().split('\t')
            times.append(time)
            values.append(float(value))

    # Создаем график
    plt.plot(times, values)
    # plt.xlabel('Время')
    plt.ylabel('Депозит')
    # plt.title('График')

    # Настраиваем подписи на оси времени
    plt.xticks(fontsize=8, rotation=45)

    # Настраиваем подписи на оси времени: с увеличенным интервалом между метками
    plt.xticks(ticks=times[::100])

    # Изменяем формат отображения чисел по вертикальной оси
    plt.gca().get_yaxis().get_major_formatter().set_scientific(False)

    # Извлекаем имя файла и путь к папке
    file_name = os.path.basename(file_path)

    # Вычисляем процентное изменение
    percentage_change = 0
    try:
        percentage_change = (values[-1] - values[0]) / values[0] * 100
    except ZeroDivisionError:
        print("Ошибка: деление на ноль")
    except IndexError:
        print("Ошибка: недостаточно элементов в списке values")
    except Exception as e:
        print("Произошла ошибка:", str(e))

    plt.title(f'{os.path.splitext(file_name)[0]} Profit: {percentage_change:.3f}%')

    file_dir = os.path.dirname(file_path)

    # Генерируем новый путь с тем же именем файла, но с расширением .png
    output_file = os.path.join(file_dir, os.path.splitext(file_name)[0] + '.png')

    # Сохраняем график в файл
    try:
        plt.savefig(output_file)
    except PermissionError as e:
        print("Ошибка при сохранении файла:", str(e))
    except Exception as e:
        print("Произошла ошибка при сохранении файла:", str(e))



if __name__ == '__main__':
    mlb.MkDirs(gNetRoot)
    gLastPrice, gDights, gTick_size = mlb.get_symbol_data(symbol, interval, cl)
    previous_candle_close = mlb.get_previous_candle_close(symbol, interval, cl)
    mlb.show_orders(symbol, gNetCode, gNetRoot, cl)
    mlb.create_candles_chart(symbol, interval, gOpenBN, gAccountBalance, gLastPrice, gNetCode, gNetRoot, cl)
    gAccountBalance, btc_balance, usdt_balance, BalanceFile = mlb.AccountBalance(gNetRoot, cl)
    mlb.plot_graph(BalanceFile)
    gSignal = round(mlb.get_signal(symbol, interval, cl).signal, 3)
    print(gSignal)
    breakpoint()


    gAccountBalance = AccountBalance()
    # print('==', gLastPrice, gDights, gTick_size)

    # breakpoint()
    #
    # AccountBalance()
    #breakpoint()

    #buyPrice = cl.book_ticker(symbol=symbol).get('askPrice')
    #print('buyPrice ='+buyPrice)
    #sellPrice = cl.book_ticker(symbol=symbol).get('bidPrice')
    #print('sellPrice ='+sellPrice)

    while True:
        #gBalance_tuple = update_balance_file(cl.account(), gBalance_tuple)
        os.system('cls' if os.name == 'nt' else 'clear')
        print('-----------------')
        try:
            #TimeCurrent = pd.to_datetime(cl.time()['serverTime'], unit='ms')

            result01 = get_macd(symbol, interval)
            gSignal = round(result01.signal, 3)
            try:
                gNetName = read_text_from_file(gNetRoot + symbol + '\\gNetName.txt')
                gNetCode = read_text_from_file(gNetRoot + symbol + '\\gNetCode.txt')
                gNetType = read_text_from_file(gNetRoot + symbol + '\\gNetType.txt')
                gOpenBN = read_text_from_file(gNetRoot + symbol + '\\gOpenBN.txt')
                gLot = read_text_from_file(gNetRoot + symbol + '\\gLot.txt')
                P0000001 = read_text_from_file(gNetRoot + symbol + '\\gNetOrd\\P0000001.txt')
                gMaxCnt = int0(read_text_from_file(gNetRoot + symbol + '\\gMaxCnt.txt'))
                str_cnt = f"{gMaxCnt:07d}"
                P9999999 = read_text_from_file(gNetRoot + symbol + '\\gNetOrd\\P' + str_cnt + '.txt')
                if P9999999 == '':
                    gMaxCnt = gMaxCnt-1
                    str_cnt = f"{gMaxCnt:07d}"
                    write_text2file(gNetRoot + symbol + '\\gMaxCnt.txt', str(gMaxCnt))
            except:
                gNetName = None
                gNetCode = None
                gNetType = None
                gOpenBN = None
                gLot = gNetLot
                P0000001 = None
                P9999999 = None
                pass

            # Получаем размер лота от размера депозита
            gAccountBalance = AccountBalance()
            if gAccountBalance != -1:
                gNetLot = round(gAccountBalance / 3367000, 5)  # 40404 / 3367000 = 0.012
                if gNetLot < 0.005:  # https://www.youtube.com/watch?v=fWYU8VAkqfo&t=1002s
                    print('gNetLot1=', gNetLot)
                    gNetLot = 0.005
                    print('gNetLot2=', gNetLot)
                    #breakpoint()

            server_time = cl.time()['serverTime']
            Time1 = datetime.datetime.fromtimestamp(server_time / 1000).strftime('%H:%M:%S')
            Time2 = datetime.datetime.now().strftime('%H:%M:%S')
            synchronize_system_time(Time1, Time2)
            Row2 = str(gSignal) + ' (' + str(gOpenLevel) + '~' + str(gCloseLevel) + ')'
            print(Row2, 'gNetCode=',  gNetCode, 'gNetName=', gNetName,
                  'gNetType=', gNetType, 'gLot=', gLot, 'P0000001=', P0000001, '=>', P9999999, '(',
                  Time1, Time2, ') gLastPrice=', gLastPrice)

            if gLast_c_value != result01.c:
                get_symbol_data(symbol)
                create_candles_chart(symbol, interval)
                # Удаление сетки при выходе через границы
                if gNetType != None and gLastPrice != None and gSignal != None and P9999999 != None and P9999999 != '':
                    # print('P9999999=', P9999999)
                    if gSignal >= gOpenLevel:
                        previous_candle_close = get_previous_candle_close(symbol, interval)
                        if previous_candle_close != None and previous_candle_close > float(P9999999):
                            gBalance_tuple = net_delete(symbol, 'shrt', symbol, gBalance_tuple)
                    if gSignal <= -gOpenLevel:
                        previous_candle_close = get_previous_candle_close(symbol, interval)
                        if previous_candle_close != None and previous_candle_close < float(P9999999):
                            gBalance_tuple = net_delete(symbol, 'long', symbol, gBalance_tuple)
                # Новая сетка
                gNetType = None
                if gSignal >= gCloseLevel:
                    gBalance_tuple = net_delete(symbol, 'long', symbol, gBalance_tuple)
                    if not os.path.isdir(gNetRoot + symbol) and gSignal >= gOpenLevel:
                        gNetName = symbol
                        gNetType = 'shrt'
                        net_make(gNetType, gStartCnt, symbol, gNetLot, gLastPrice, gNetStep, gTP_pips)
                if gSignal <= -gCloseLevel:
                    gBalance_tuple = net_delete(symbol, 'shrt', symbol, gBalance_tuple)
                    if not os.path.isdir(gNetRoot + symbol) and gSignal <= -gOpenLevel:
                        gNetName = symbol
                        gNetType = 'long'
                        net_make(gNetType, gStartCnt, symbol, gNetLot, gLastPrice, gNetStep, gTP_pips)
                gLast_c_value = result01.c

            # breakpoint()
            net_support(symbol)
            #create_candles_chart(symbol, interval)
            time.sleep(2)  # Пауза в 500 миллисекунд
            # breakpoint()
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            time.sleep(60)
            cl = Spot(api_key=api_key, api_secret=api_secret, base_url=base_url)  # Ctrl+Left_Click по Spot
            # ВЕРСИЯ 1