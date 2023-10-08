import os
import datetime
import openpyxl
from bokeh.plotting import figure, output_file, save
from bokeh.io import export_png
from bokeh.models import LinearAxis, Range1d, Label
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.tools import HoverTool


def create_balance_chart(gNetRoot, strAccountBalanceFix, strAccountBalanceFloat):
    print('create_balance_chart: strAccountBalanceFix=', strAccountBalanceFix, 'strAccountBalanceFloat=', strAccountBalanceFloat)

    # path = os.path.join(gNetRoot, "Balance", datetime.datetime.now().strftime("%Y-%m-%d"))
    path = os.path.join(gNetRoot, "Balance", datetime.datetime.now().strftime("%Y"))
    if not os.path.exists(path):
        os.makedirs(path)

    path_html = os.path.join(gNetRoot, "Balance", 'html')
    if not os.path.exists(path_html):
        os.makedirs(path_html)

    output_file(os.path.join(path_html, datetime.datetime.now().strftime('%Y-%m-%d') + ".html"))  # Указываем выходной файл

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    line = f'{timestamp}\t{strAccountBalanceFix}\t{strAccountBalanceFloat}\n'

    BalanceFile = os.path.join(gNetRoot, "Balance", datetime.datetime.now().strftime('%Y-%m-%d') + '.txt')
    with open(BalanceFile, 'a', encoding='utf-8') as file:
        file.write(line)

    # Чтение данных из файла
    timestamps = []
    balances_fix = []
    balances_float = []

    with open(BalanceFile, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            timestamps.append(parts[0])
            balances_fix.append(float(parts[1]))
            balances_float.append(float(parts[2]))

    # Преобразование временных меток в объекты datetime
    timestamps = [datetime.datetime.strptime(time, "%H:%M:%S") for time in timestamps]

    # Создание фигуры
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%d.%m.%Y %H:%M:%S')
    p = figure(title="Баланс счета Козлов Алексей Викторович на " + formatted_datetime, width=1280, height=1024, output_backend="svg")

    # p = figure(title="Баланс счета на " + datetime.datetime.now().strftime('%Y-%m-%d'), width=1280, height=1024, output_backend="svg")

    # Добавление линий на фигуру
    line_fix = p.line(timestamps, balances_fix, legend_label="Фиксированный баланс", line_color="blue")
    line_float = p.line(timestamps, balances_float, legend_label="Плавающий баланс", line_color="red")

    # Добавление последних значений баланса в качестве аннотаций
    last_balance_fix = balances_fix[-1]
    last_balance_float = balances_float[-1]
    p.add_layout(Label(x=timestamps[-1], y=last_balance_fix, text=str(last_balance_fix), text_font_size="10pt", text_color="blue", x_offset=10, y_offset=10))
    p.add_layout(Label(x=timestamps[-1], y=last_balance_float, text=str(last_balance_float), text_font_size="10pt", text_color="red", x_offset=10, y_offset=-20))

    # Добавление первых значений баланса в качестве аннотаций
    first_balance_fix = balances_fix[0]
    first_balance_float = balances_float[0]
    p.add_layout(Label(x=timestamps[0], y=first_balance_fix, text=str(first_balance_fix), text_font_size="10pt", text_color="blue", x_offset=-50, y_offset=10))
    p.add_layout(Label(x=timestamps[0], y=first_balance_float, text=str(first_balance_float), text_font_size="10pt", text_color="red", x_offset=-50, y_offset=-20))

    # Установка минимального значения на оси y
    min_balance = min(balances_fix + balances_float)
    max_balance = max(balances_fix + balances_float)
    p.y_range = Range1d(min_balance - 0.1 * (max_balance - min_balance), max_balance + 0.1 * (max_balance - min_balance))

    # Создание новой оси y справа
    p.extra_y_ranges = {"right_axis": Range1d(start=min_balance - 0.1 * (max_balance - min_balance), end=max_balance + 0.1 * (max_balance - min_balance))}
    p.add_layout(LinearAxis(y_range_name="right_axis"), 'right')

    # Добавление горизонтальных линий на правой оси
    p.line([timestamps[0], timestamps[-1]], [last_balance_fix, last_balance_fix], line_color="blue", line_dash="dashed", y_range_name="right_axis")
    p.line([timestamps[0], timestamps[-1]], [last_balance_float, last_balance_float], line_color="red", line_dash="dashed", y_range_name="right_axis")

    # Добавление меток процентов на левой стороне
    p.add_layout(Label(x=timestamps[0], y=first_balance_fix, text="0%", text_font_size="10pt", text_color="blue", x_offset=-70, y_offset=10))
    p.add_layout(Label(x=timestamps[0], y=first_balance_float, text="0%", text_font_size="10pt", text_color="red", x_offset=-70, y_offset=-20))
    # p.add_layout(Label(x=timestamps[-1], y=last_balance_fix, text=f"{(last_balance_fix - first_balance_fix) / first_balance_fix * 100:.2f}%", text_font_size="10pt", text_color="blue", x_offset=-70, y_offset=10))
    # p.add_layout(Label(x=timestamps[-1], y=last_balance_float, text=f"{(last_balance_float - first_balance_float) / first_balance_float * 100:.2f}%", text_font_size="10pt", text_color="red", x_offset=-70, y_offset=-20))

    # Форматирование меток оси x в формате времени на немецком языке
    p.xaxis.formatter = DatetimeTickFormatter(
        hours="%H:%M:%S",
        days="%d.%m.%Y",
        months="%m.%Y",
        years="%Y"
    )

    # Добавление легенды
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    p.legend.label_text_font_size = "10pt"

    # Добавление всплывающих подсказок
    line_fix.hover_glyph = line_fix.glyph
    line_fix.nonselection_glyph = line_fix.glyph
    line_float.hover_glyph = line_float.glyph
    line_float.nonselection_glyph = line_float.glyph
    p.add_tools(HoverTool(renderers=[line_fix, line_float], tooltips=[("Временная метка", "@x{%F %T}"), ("Фиксированный баланс", "@y{0.00}"), ("Плавающий баланс", "@y{0.00}")], formatters={"@x": "datetime"}))

    # Расчет изменения в процентах
    percentage_change_fix = (last_balance_fix - first_balance_fix) / first_balance_fix * 100
    percentage_change_float = (last_balance_float - first_balance_float) / first_balance_float * 100

    # Добавление меток процентов над линией
    p.add_layout(Label(x=timestamps[-1], y=last_balance_fix,
                       text=f"{percentage_change_fix:.2f}%",
                       text_font_size="10pt", text_color="green", x_offset=10, y_offset=30))
    p.add_layout(Label(x=timestamps[-1], y=last_balance_float,
                       text=f"{percentage_change_float:.2f}%",
                       text_font_size="10pt", text_color="green", x_offset=10, y_offset=-10))

    # Сохранение графика
    save(p)

    # Сохранение графика в виде графического файла
    # filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = datetime.datetime.now().strftime("%Y-%m-%d")
    export_png(p, filename=os.path.join(path, f"{filename}.png"))

    # Округление значений до 2 знаков после запятой
    rounded_percentage_change_float = round(percentage_change_float, 2)
    rounded_percentage_change_fix = round(percentage_change_fix, 2)

    # Создание имени файла
    filename = f"{rounded_percentage_change_float}.xlsx"

    # Удаление одной директории справа из пути
    parent_directory = os.path.dirname(path)

    # Объединение родительской директории и имени файла
    filepath = os.path.join(parent_directory, filename)

    # Создание списка значений для записи
    values = []

    # Проверка наличия файла
    if not os.path.exists(filepath):
        print('create_balance_chart: Создание нового файла XLSX')
        workbook = openpyxl.Workbook()
        sheet = workbook.active
    else:
        print('create_balance_chart: Открытие существующего файла XLSX')
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active

    # Добавление нового значения в список
    values.append(rounded_percentage_change_fix)

    sheet.append(values)

    # Сохранение файла XLSX
    workbook.save(filepath)
