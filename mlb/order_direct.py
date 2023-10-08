from binance.error import ClientError
import mlb


def is_order_by_T(symbol, T, cl):
    try:
        cl.get_order(symbol, origClientOrderId=T)
        return True
    except ClientError:
        return False


def get_status_buy_order_by_T(symbol, T, cl):
    try:
        order = cl.get_order(symbol, origClientOrderId=T)
        if order["side"] == "BUY":
            return order["status"]
        return 'EMPTY'
    except ClientError:
        return 'EMPTY'


def get_status_sell_order_by_T(symbol, T, cl):
    try:
        order = cl.get_order(symbol, origClientOrderId=T)
        if order["side"] == "SELL":
            return order["status"]
        return 'EMPTY'
    except ClientError:
        return 'EMPTY'


def send_limit_order(symbol, side, gLot, P, T, cl, prichina):
    print('\nsend_limit_order:', symbol, side, gLot, P, T, prichina)
    if P == '':
        print(prichina, 'send_limit_order: P=', P)
        return -1
    P = round(float(P), 6)
    gLot = float(gLot)  # Convert gLot to float
    gLot = "{:.6f}".format(gLot)  # убираем 9e-05
    # mlb.write_to_tab_xls_file('send_limit_order', symbol, gLot, str(P), T, side)
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


def send_market_order(symbol, side, gLot, P, cl, T):
    gLot = float(gLot)  # Convert gLot to float
    gLot = "{:.6f}".format(gLot)  # убираем 9e-05
    mlb.write_to_tab_xls_file('send_market_order', symbol, gLot, P, T, side)
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
