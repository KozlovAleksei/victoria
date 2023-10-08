import time
import datetime

def write_text2file(filename_w, text_w):
    for t in range(1, 2000):
        try:
            with open(filename_w, 'w') as file_handle:
                file_handle.write(str(text_w))
            break
        except:
            time.sleep(0.01)  # 20 секунд выполнения
            continue
    return


def read_text_from_file(TextFileName):
    for _ in range(3):
        try:
            with open(TextFileName, "r") as file:
                text = file.read()
                return text
        except FileNotFoundError:
            time.sleep(0.01)
    return ''


def write_to_tab_xls_file(filename, *args):

    #deals('Deals.xls', g1, g2, g3, g4, g5, g6)
    #deals('Deals.xls', g1, g2, g3, g4, g5, g6, g7, g8)

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    line = f'{timestamp}\t'

    # Объединяем все аргументы в строку с разделителем '\t'
    line += '\t'.join(str(arg) for arg in args)
    line += '\n'

    print(line)

    with open(filename, 'a', encoding='utf-8') as file:
        file.write(line)
