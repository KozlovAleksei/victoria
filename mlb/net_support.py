import mlb
import os
import time

def net_support(gNetName, gNetCode, gNetRoot, symbol, interval, gLastPrice, gStartCnt, cl):
    print('net_support:', gNetName, gNetCode, gNetRoot, symbol, gStartCnt)
    if gNetCode is None:
        return
    gNetFolder = gNetRoot + gNetName + '\\'
    gNetOrd = gNetFolder + 'gNetOrd\\'
    gMaxCnt = mlb.str2int(mlb.read_text_from_file(gNetFolder + 'gMaxCnt.txt'))

    def set_gMaxCnt():
        print('net_support:set_gMaxCnt')
        gNetFolder = gNetRoot + gNetName + '\\'
        gNetOrd = gNetFolder + 'gNetOrd\\'
        fileCount = 0
        for _, _, files in os.walk(gNetOrd):
            for file in files:
                if file != "." and file != "..":
                    fileCount += 1
        gMaxCnt = fileCount // 3
        mlb.write_text2file(gNetFolder + 'gMaxCnt.txt', str(gMaxCnt))

    gNetType = mlb.read_text_from_file(gNetFolder + 'gNetType.txt')
    for cnt in range(1, gMaxCnt + 1):
        print(cnt, end=' ')
        str_cnt = f"{cnt:07d}"
        # P = mlb.read_text_from_file(gNetOrd + 'P' + str_cnt + '.txt')

        # askPrice = cl.book_ticker(symbol=symbol).get('askPrice')
        # print('askPrice ='+askPrice)
        # bidPrice = cl.book_ticker(symbol=symbol).get('bidPrice')
        # print('bidPrice ='+bidPrice)

        # if gNetType == 'long' and gLastPrice > float(P):
        #     continue
        #
        # if gNetType == 'shrt' and gLastPrice < float(P):
        #     continue

        T = mlb.read_text_from_file(gNetOrd + 'T' + str_cnt + '.txt')

        # print('Выставляю ордера, если не выставлены')
        if gNetType == 'long' and not mlb.is_order_by_T(symbol, f"{T}1", cl):
            gLot = mlb.read_text_from_file(gNetFolder + 'gLot.txt')
            P = mlb.read_text_from_file(gNetOrd + 'P' + str_cnt + '.txt')
            RetCode = mlb.send_limit_order(symbol, 'BUY', gLot, P, f"{T}1", cl, f"New long P{str_cnt}.txt={P}")
            # if RetCode == -1:
            #     set_gMaxCnt()
            #     return
            if RetCode == -2010 and gMaxCnt == gStartCnt:  # Account has insufficient balance for requested action.
                print('Урезаю long массив до', cnt)
                for cnt2 in range(cnt, gStartCnt + 1):
                    print('cnt2=', cnt2)
                    if cnt2 > 10:
                        str_cnt2 = f"{cnt2:07d}"
                        T2 = mlb.read_text_from_file(gNetOrd + 'T' + str_cnt2 + '.txt')
                        # print('len(T2)=', len(T2), ' ~ ', T2)
                        if len(T2) == 9 and not mlb.is_order_by_T(symbol, f"{T2}1", cl):
                            # print('Удаляю избыточные файлы long ' + str_cnt2)
                            os.remove(gNetOrd + 'T' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'P' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'F' + str_cnt2 + '.txt')
                set_gMaxCnt()
                return
            if RetCode == -2010:
                time.sleep(1.1)
                mlb.ReBalanceAccount(symbol, interval, gLastPrice, gNetCode, gNetRoot, cl, 'net_support')
                return
                pass

        if gNetType == 'shrt' and not mlb.is_order_by_T(symbol, f"{T}2", cl):
            gLot = mlb.read_text_from_file(gNetFolder + 'gLot.txt')
            P = mlb.read_text_from_file(gNetOrd + 'P' + str_cnt + '.txt')
            RetCode = mlb.send_limit_order(symbol, 'SELL', gLot, P, f"{T}2", cl, f"New shrt P{str_cnt}.txt={P}")
            # if RetCode == -1:
            #     set_gMaxCnt()
            #     return
            if RetCode == -2010 and gMaxCnt == gStartCnt:  # Account has insufficient balance for requested action.
                print('Урезаю shrt массив до', cnt)
                for cnt2 in range(cnt, gStartCnt + 1):
                    # print('cnt2=', cnt2)
                    if cnt2 > 10:
                        str_cnt2 = f"{cnt2:07d}"
                        T2 = mlb.read_text_from_file(gNetOrd + 'T' + str_cnt2 + '.txt')
                        # print('len(T2)=', len(T2), ' ~ ', T2)
                        if len(T2) == 9 and not mlb.is_order_by_T(symbol, f"{T2}2", cl):
                            print('Удаляю избыточные файлы shrt ' + str_cnt2)
                            os.remove(gNetOrd + 'T' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'P' + str_cnt2 + '.txt')
                            os.remove(gNetOrd + 'F' + str_cnt2 + '.txt')
                set_gMaxCnt()
                return
            if RetCode == -2010:
                time.sleep(1.1)
                mlb.ReBalanceAccount(symbol, interval, gLastPrice, gNetCode, gNetRoot, cl, 'net_support')
                return
                pass

        # print('Чекаю ордера и выставляю TP, если его нет.')
        if gNetType == 'long' and not mlb.is_order_by_T(symbol, f"{T}3", cl) \
            and mlb.get_status_buy_order_by_T(symbol, f"{T}1", cl) == 'FILLED':
                gLot = mlb.read_text_from_file(gNetFolder + 'gLot.txt')
                F = mlb.read_text_from_file(gNetOrd + 'F' + str_cnt + '.txt')
                mlb.send_limit_order(symbol, 'SELL', gLot, F, f"{T}3", cl, f"TP for long F{str_cnt}.txt={F}")

        if gNetType == 'shrt' and not mlb.is_order_by_T(symbol, f"{T}4", cl) \
            and mlb.get_status_sell_order_by_T(symbol, f"{T}2", cl) == 'FILLED':
                gLot = mlb.read_text_from_file(gNetFolder + 'gLot.txt')
                F = mlb.read_text_from_file(gNetOrd + 'F' + str_cnt + '.txt')
                mlb.send_limit_order(symbol, 'BUY', gLot, F, f"{T}4", cl, f"TP for shrt F{str_cnt}.txt={F}")

        # print('Чекаю TP, если исполнен, то делаю новый trans_id')
        if gNetType == 'long' and mlb.get_status_sell_order_by_T(symbol, f"{T}3", cl) == 'FILLED':
            filename = gNetOrd + 'T' + str_cnt + '.txt'
            while os.path.isfile(filename):
                os.remove(filename)
            new_T = gNetCode+mlb.get_str_rnd(4)
            mlb.write_text2file(filename, new_T)
            check_T = mlb.read_text_from_file(filename)
            while check_T != new_T:
                mlb.write_text2file(filename, new_T)
                check_T = mlb.read_text_from_file(filename)

        if gNetType == 'shrt' and mlb.get_status_buy_order_by_T(symbol, f"{T}4", cl) == 'FILLED':
            filename = gNetOrd + 'T' + str_cnt + '.txt'
            new_T = gNetCode+mlb.get_str_rnd(4)
            mlb.write_text2file(filename, new_T)
            check_T = mlb.read_text_from_file(filename)
            while check_T != new_T:
                mlb.write_text2file(filename, new_T)
                check_T = mlb.read_text_from_file(filename)
    return
