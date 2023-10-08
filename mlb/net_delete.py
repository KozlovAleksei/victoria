import mlb
import os
import time
import shutil


def net_delete(gNetName, gNetType, symbol, gNetRoot, cl):
    print("net_delete:", gNetName, gNetType, symbol, gNetRoot, cl)
    gNetFolder = gNetRoot + gNetName + '\\'
    if not os.path.isdir(gNetFolder):  # если нет папки сетки, то возврат
        print('net_delete: Папки нет')
        return 'net_delete: Папки нет'
    if mlb.read_text_from_file(gNetFolder + 'gNetType.txt') != gNetType:  # отбрасываем сетку с ненужным направлением
        print('net_delete: Отброшена сетка ' + gNetType)
        return 'net_delete: Отброшена сетка ' + gNetType
    try:
        cl.cancel_open_orders(symbol, recvWindow=59000)
    except:
        pass
    print(gNetFolder)
    shutil.rmtree(gNetFolder)  # удаляем папку сети
    while os.path.isdir(gNetFolder):
        print('net_delete: Не смог удалить папку',gNetFolder)
        shutil.rmtree(gNetFolder)  # удаляем папку сети
        time.sleep(0.5)  # Пауза в 500 миллисекунд
    time.sleep(1)  # Пауза в 1 сек
    try:
        cl.cancel_open_orders(symbol, recvWindow=59000)
    except:
        print('net_delete: Сетка удалена')
        return 'net_delete: Сетка удалена'
        pass

    print('net_delete: Ордера не удалены')
    return 'net_delete: Ордера не удалены'
