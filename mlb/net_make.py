import mlb
import os


def net_make(gNetType, gMaxCnt, symbol, gLot, gNetStep, gTP_pips, gNetRoot, interval, cl):
    gLastPrice, gDights, gTick_size = mlb.get_symbol_data(symbol, interval, cl)
    gNetName = symbol
    gNetCode = gNetType[0]+mlb.get_str_rnd(4)
    print('net_make:', gNetName, gNetCode, gNetType, gMaxCnt, symbol, gLot, gNetStep, gTP_pips, gLastPrice)
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
    mlb.write_text2file(gNetFolder + 'gNetName.txt', gNetName)
    mlb.write_text2file(gNetFolder + 'gNetCode.txt', gNetCode)
    mlb.write_text2file(gNetFolder + 'gNetType.txt', gNetType)
    mlb.write_text2file(gNetFolder + 'gMaxCnt.txt', str(gMaxCnt))
    mlb.write_text2file(gNetFolder + 'symbol.txt', symbol)
    mlb.write_text2file(gNetFolder + 'gLot.txt', str(gLot))
    mlb.write_text2file(gNetFolder + 'gNetStep.txt', str(gNetStep))
    mlb.write_text2file(gNetFolder + 'gTP_pips.txt', str(gTP_pips))
    mlb.write_text2file(gNetFolder + 'gLastPrice.txt', str(gLastPrice))
    price_up = gLastPrice
    price_dn = gLastPrice
    SL_pice = None

    for cnt in range(1, gMaxCnt + 1):
        str_cnt = f"{cnt:07d}"
        mlb.write_text2file(gNetOrd + 'T' + str_cnt + '.txt', gNetCode+mlb.get_str_rnd(4))
        price_dn = round(float(price_dn), gDights)
        price_up = round(float(price_up), gDights)

        if gNetType == 'long':
            price_dn = round(price_dn - (gTick_size * gNetStep), gDights)
            mlb.write_text2file(gNetOrd + 'P' + str_cnt + '.txt', price_dn)
            mlb.write_text2file(gNetOrd + 'F' + str_cnt + '.txt', round(price_dn + (gTick_size * gTP_pips), gDights))
            SL_pice = round(price_dn - (gTick_size * gTP_pips), gDights)

        if gNetType == 'shrt':
            price_up = round(price_up + (gTick_size * gNetStep), gDights)
            mlb.write_text2file(gNetOrd + 'P' + str_cnt + '.txt', price_up)
            mlb.write_text2file(gNetOrd + 'F' + str_cnt + '.txt', round(price_up - (gTick_size * gTP_pips), gDights))
            SL_pice = round(price_up + (gTick_size * gTP_pips), gDights)

    mlb.write_text2file(gNetFolder + 'gSL_L.txt', SL_pice)
    mlb.write_text2file(gNetFolder + 'gSL_T.txt', gNetCode+mlb.get_str_rnd(4))

    # mlb.ReBalanceAccount(symbol, interval, gLastPrice, gNetCode, gNetRoot, cl, 'net_make')

    gAccountBalance, btc_balance, usdt_balance, BalanceFile = mlb.AccountBalance(gNetRoot, cl)
    round(gAccountBalance, 2), round(btc_balance, 6), round(usdt_balance, 2), BalanceFile

    mlb.write_text2file(gNetFolder + 'gOpenBN.txt', str(int(gAccountBalance)))
    # breakpoint()
    return gNetCode
