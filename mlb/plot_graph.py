import matplotlib.pyplot as plt
import os

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
