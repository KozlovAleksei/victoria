import datetime

def AccountBalance(gNetRoot, cl):
    print('AccountBalance')
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

        BalanceFile = gNetRoot + datetime.datetime.now().strftime('%d-%m-%Y') + '.txt'
        with open(BalanceFile, 'a', encoding='utf-8') as file:
            file.write(line)
        #plot_graph(filename)
        
        return round(gAccountBalance, 2), round(btc_balance, 6), round(usdt_balance, 2), BalanceFile

    return -1, -1,  -1, 'NoFile'
