import time
import random
import string
import uuid


def get_str_rnd(cnt=8):

    def get_str_rnd1(cnt):
        allowed_chars = string.digits + string.ascii_letters
        return ''.join(random.choices(allowed_chars, k=cnt))

    def get_str_rnd2(cnt):

        def RetCode():
            current_time = int(time.time() * 1000)  # Получение текущего времени в миллисекундах
            random.seed(current_time)  # Установка seed для генератора случайных чисел
            characters = string.digits + string.ascii_letters  # Цифры и латинские буквы
            return ''.join(random.choice(characters) for _ in range(cnt))

        while True:
            RetCode1 = RetCode()

            time.sleep(0.001)

            RetCode2 = RetCode()

            if RetCode1 != RetCode2:
                return RetCode2
            time.sleep(0.1)

    rnd1 = get_str_rnd1(cnt)
    rnd2 = get_str_rnd2(cnt)

    if rnd1 != rnd2:
        return rnd2


def get_num_rnd(cnt=8):

    def get_num_rnd1(cnt):
        return str(uuid.uuid4())[:cnt]


    def get_num_rnd2(cnt):

        if cnt is None:
            cnt = 8

        def RetCode():
            current_time = int(time.time() * 1000)  # Получение текущего времени в миллисекундах
            random.seed(current_time)  # Установка seed для генератора случайных чисел

            RetCode = str(random.randint(1, 9))

            for x in range(2, cnt + 1):
                RetCode += str(random.randint(0, 9))

            return RetCode

        while True:
            current_time = int(time.time() * 1000)  # Получение текущего времени в миллисекундах
            random.seed(current_time)  # Установка seed для генератора случайных чисел

            RetCode1 = RetCode()

            time.sleep(0.001)

            RetCode2 = RetCode()

            if RetCode1 != RetCode2:
                return RetCode2
            time.sleep(0.1)

    rnd1 = get_num_rnd1(cnt)
    rnd2 = get_num_rnd2(cnt)

    if rnd1 != rnd2:
        return rnd2


def str2int(str1):
    try:
        return int(str1)
    except ValueError:
        return -1
