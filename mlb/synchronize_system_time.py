import datetime
import subprocess
import random


def synchronize_system_time(time_to_sync, current_time):
    """
    Функция синхронизирует системное время с указанным временем.

    Args:
        time_to_sync (str): Время для синхронизации в формате "ЧЧ:ММ:СС".
        current_time (str): Текущее системное время в формате "ЧЧ:ММ:СС".

    Returns:
        bool: True, если системное время успешно синхронизировано, False в противном случае.
    """

    if time_to_sync != current_time:
        time_difference = datetime.datetime.strptime(time_to_sync, "%H:%M:%S") - datetime.datetime.strptime(current_time, "%H:%M:%S")

        # Определяем, в какую сторону нужно сдвинуть время
        if time_difference.total_seconds() < 0:
            time_shift = "+" + str(abs(time_difference.seconds))
        else:
            time_shift = "-" + str(abs(time_difference.seconds))

        # Список серверов для выбора
        servers = [
            "time.windows.com",
            "time.nist.gov",
            "time-nw.nist.gov",
            "time-a.nist.gov",
            "time-b.nist.gov"
        ]

        # Случайный выбор сервера
        selected_server = random.choice(servers)

        print('selected_server=', selected_server)

        try:
            # Вызов команды для синхронизации времени с выбранным сервером
            subprocess.run(
                [
                    "w32tm", "/resync", "/force",
                    f"/manualpeerlist:{selected_server}",
                    "/syncfromflags:manual", "/update",
                    f"/adjustphase:{time_shift}"
                ]
            )
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при синхронизации времени: {e}")
            return False

        # Проверяем, что системное время успешно синхронизировано
        updated_time = datetime.datetime.now().strftime("%H:%M:%S")
        if updated_time == current_time:
            print("Системное время успешно синхронизировано!")
            return True
        else:
            print("Не удалось синхронизировать системное время.")
            return False
