"""
mainHeaven.py — главный файл запуска и интерактивного меню выбора заездов (1–9)
для хаба SPIKE Prime команды Heaven.
"""

from Base import *
from Heaven_1 import run_1
from Heaven_2 import run_2
from Heaven_3 import run_3
from Heaven_4 import run_4
from Heaven_5 import run_5
from Heaven_6 import run_6
from Heaven_7 import run_7
from Heaven_8 import run_8
from Heaven_9 import run_9


# ==============================================================================
# 1. РЕЕСТР ЗАЕЗДОВ (1–9)
# ==============================================================================
RUNS = [
    run_1,
    run_2,
    run_3,
    run_4,
    run_5,
    run_6,
    run_7,
    run_8,
    run_9,
]


# ==============================================================================
# 2. КРУПНЫЕ ЦИФРЫ 5x3 И ИКОНКИ СОСТОЯНИЙ ДЛЯ МАТРИЦЫ ХАБА
# ==============================================================================
DIGITS_5x3 = [
    # 1
    Matrix([
        [0, 0, 100, 0, 0],
        [0, 100, 100, 0, 0],
        [0, 0, 100, 0, 0],
        [0, 0, 100, 0, 0],
        [0, 100, 100, 100, 0],
    ]),
    # 2
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 0, 0, 0],
        [0, 100, 100, 100, 0],
    ]),
    # 3
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 100, 100, 100, 0],
    ]),
    # 4
    Matrix([
        [0, 100, 0, 100, 0],
        [0, 100, 0, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 0, 0, 100, 0],
    ]),
    # 5
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 100, 0, 0, 0],
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 100, 100, 100, 0],
    ]),
    # 6
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 100, 0, 0, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 0, 100, 0],
        [0, 100, 100, 100, 0],
    ]),
    # 7
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 0, 0, 100, 0],
    ]),
    # 8
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 100, 0, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 0, 100, 0],
        [0, 100, 100, 100, 0],
    ]),
    # 9
    Matrix([
        [0, 100, 100, 100, 0],
        [0, 100, 0, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 0, 0, 100, 0],
        [0, 100, 100, 100, 0],
    ]),
]

# Иконка старта (стрелка вправо)
ICON_GO = Matrix([
    [0, 100, 0, 0, 0],
    [0, 100, 100, 0, 0],
    [0, 100, 100, 100, 0],
    [0, 100, 100, 0, 0],
    [0, 100, 0, 0, 0],
])

# Иконка успешного финиша (галочка)
ICON_OK = Matrix([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 100],
    [0, 0, 0, 100, 0],
    [100, 0, 100, 0, 0],
    [0, 100, 0, 0, 0],
])


# ==============================================================================
# 3. МЕЛОДИЯ ЗАВЕРШЕНИЯ МИССИИ
# ==============================================================================
VICTORY_MELODY = ["C5/8", "E5/8", "G5/8", "C6/4"]


def play_finish_melody():
    """Проигрывает короткую победную мелодию после успешного финиша заезда."""
    try:
        hub.speaker.volume(80)
        hub.speaker.play_notes(VICTORY_MELODY, tempo=180)
    except Exception:
        pass


# ==============================================================================
# 4. ГЛАВНЫЙ ЦИКЛ МЕНЮ (NVRAM + ЗАЩИТА ОТ ОШИБОК + ПОЛНАЯ ОСТАНОВКА МОТОРОВ)
# ==============================================================================
def run_menu():
    """Соревновательное меню выбора 9 заездов на хабе SPIKE Prime."""
    total_runs = len(RUNS)
    max_index = total_runs - 1

    # Восстанавливаем последний выбранный заезд из памяти хаба (NVRAM)
    try:
        saved = hub.system.storage(0, 1)
        if saved and saved[0] <= max_index:
            current_index = saved[0]
        else:
            current_index = 0
    except Exception:
        current_index = 0

    print("=== HEAVEN MENU READY ===")
    print_battery()
    hub.light.on(Color.BLUE)

    while True:
        hub.display.icon(DIGITS_5x3[current_index])

        # Ждём нажатия любой кнопки
        pressed = set()
        while not pressed:
            pressed = hub.buttons.pressed()
            wait(25)

        # ВЛЕВО: предыдущий заезд (циклично 1 -> 9)
        if Button.LEFT in pressed:
            current_index = (current_index - 1) % total_runs
            try:
                hub.system.storage(0, bytes([current_index]))
            except Exception:
                pass
            while any(hub.buttons.pressed()):
                wait(10)

        # ВПРАВО: следующий заезд (циклично 9 -> 1)
        elif Button.RIGHT in pressed:
            current_index = (current_index + 1) % total_runs
            try:
                hub.system.storage(0, bytes([current_index]))
            except Exception:
                pass
            while any(hub.buttons.pressed()):
                wait(10)

        # ЦЕНТР: запуск выбранного заезда
        elif Button.CENTER in pressed:
            # Ждём отпускания кнопки, чтобы избежать случайного двойного старта
            while any(hub.buttons.pressed()):
                wait(10)

            set_heading(0.0)
            hub.light.on(Color.MAGENTA)
            hub.display.icon(ICON_GO)
            wait(120)

            try:
                RUNS[current_index]()
                stop_all()
                hub.light.on(Color.GREEN)
                hub.display.icon(ICON_OK)
                play_finish_melody()
                wait(150)
            except Exception as e:
                stop_all()
                print("ОШИБКА В ЗАЕЗДЕ №{}: {}".format(current_index + 1, e))
                hub.light.on(Color.RED)
                wait(1000)

            hub.light.on(Color.BLUE)


# ==============================================================================
# 5. ТОЧКА ВХОДА
# ==============================================================================
if __name__ == "__main__":
    run_menu()