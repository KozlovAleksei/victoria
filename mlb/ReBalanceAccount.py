import mlb

def ReBalanceAccount(symbol, interval, gLastPrice, gNetCode, gNetRoot, cl, prichina):
    return
    print('ReBalanceAccount:', prichina)
    if gLastPrice == None or gNetCode == None:
        return
    btc_balance = None
    usdt_balance = None
    print('ReBalanceAccount')
    gLastPrice, gDights, gTick_size = mlb.get_symbol_data(symbol, interval, cl)
    json_data = cl.account()
    for balance in json_data['balances']:
        if balance['asset'] == 'BTC':
            btc_balance = float(balance['free']) + float(balance['locked'])
        elif balance['asset'] == 'USDT':
            usdt_balance = float(balance['free']) + float(balance['locked'])
    print('btc_balance', btc_balance)
    print('usdt_balance', usdt_balance)
    print('gLastPrice', gLastPrice)
    if btc_balance is not None and usdt_balance is not None:
        filename = gNetRoot + "Orders\\" + gNetCode + "_RB.txt"
        print('ReBalanceAccount: gLastPrice=', gLastPrice)
        BTC_in_USDT=btc_balance * gLastPrice  # Количество BTC в долларах
        if BTC_in_USDT > usdt_balance: #  Продать BTC
            sell_summ_usd = (BTC_in_USDT - usdt_balance) / 2
            BTC_to_sell = sell_summ_usd / gLastPrice
            if BTC_to_sell >= 0.001:
                try:
                    mlb.send_market_order(symbol, 'SELL', round(BTC_to_sell, 6), 'Market', cl, 'ReBalance')
                    mlb.write_text2file(filename, 'SELL Market BTC at price=' + str(gLastPrice) + 'QTY=' + str(round(BTC_to_sell, 6)))
                except Exception as e:
                    print("Произошла ошибка при SELL-ReBalance:", e)
        if BTC_in_USDT < usdt_balance: #  Купить BTC
            buy_summ_usd = (usdt_balance - BTC_in_USDT) / 2
            BTC_to_buy = round(buy_summ_usd / gLastPrice, 6)
            if BTC_to_buy >= 0.001:
                try:
                    mlb.send_market_order(symbol, 'BUY', round(BTC_to_buy, 6), 'Market', cl, 'ReBalance')
                    mlb.write_text2file(filename, 'BUY Market BTC at price=' + str(gLastPrice) + 'QTY=' + str(round(BTC_to_buy, 6)))
                except Exception as e:
                    print("Произошла ошибка при BUY-ReBalance:", e)
    return
