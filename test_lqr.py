"""
test_lqr.py — тестовый заезд для калибровки LQR-регулятора поворотов.
Показывает стартовый курс (0.0°), изменение угла в реальном времени при поворотах
направо, налево и одним колесом (pivot), а в конце выводит перелёт/недоворот
и время поворота.
"""

from Base import *
from turning import _voltage_scale, _clamp

# ==============================================================================
# 1. КОЭФФИЦИЕНТЫ ДЛЯ ПОДБОРА (Меняй здесь, когда найдёшь идеал — перенеси в config.py)
# ==============================================================================
# Танковый разворот (обоими колёсами)
TEST_TURN_K1 = TURN_K1              # Жёсткость доводки по углу (начни с 2.0 - 2.8)
TEST_TURN_K2 = TURN_K2              # Гашение инерции по gyro_z (начни с 0.12 - 0.25)
TEST_TURN_MIN_POWER = TURN_MIN_POWER  # Мин. мощность страгивания на финише (12 - 18)
TEST_TURN_TOL = TURN_TOLERANCE      # Допуск остановки в градусах (0.5 - 1.0)

# Одноколёсный поворот (pivot)
TEST_PIVOT_K1 = PIVOT_K1            # Жёсткость для одного колеса (начни с 3.0 - 4.0)
TEST_PIVOT_K2 = PIVOT_K2            # Демпфер для одного колеса (начни с 0.20 - 0.35)
TEST_PIVOT_MIN_POWER = PIVOT_MIN_POWER
TEST_PIVOT_TOL = PIVOT_TOLERANCE

# Параметры тестовых поворотов
TEST_POWER = 70                     # Максимальная мощность теста
TEST_ANGLES = [90, -90, 180]        # Серия углов для танкового поворота (+ вправо, - влево)
TEST_PIVOT = True                  # Поставь True, чтобы дополнительно протестировать pivot


def turn_lqr_debug(
    power,
    angle,
    pivot=None,
    k1=None,
    k2=None,
    min_power=None,
    tolerance=None,
    timeout_ms=2000,
):
    """
    Точная копия алгоритма turn() из turning.py с выводом угла, ошибки,
    угловой скорости и мощности в терминал каждые 40 мс.
    """
    drive_base.stop()

    is_pivot = pivot in (LEFT, RIGHT)
    gain_k1 = k1 if k1 is not None else (TEST_PIVOT_K1 if is_pivot else TEST_TURN_K1)
    gain_k2 = k2 if k2 is not None else (TEST_PIVOT_K2 if is_pivot else TEST_TURN_K2)
    p_min = min_power if min_power is not None else (TEST_PIVOT_MIN_POWER if is_pivot else TEST_TURN_MIN_POWER)
    tol = tolerance if tolerance is not None else (TEST_PIVOT_TOL if is_pivot else TEST_TURN_TOL)
    p_max = abs(power)

    start_heading = hub.imu.heading()
    state.heading = wrap_angle(state.heading + float(angle))
    target_heading = state.heading

    v_scale = _voltage_scale()
    timer = StopWatch()
    last_print_ms = 0

    max_overshoot = 0.0
    turn_sign = 1 if angle >= 0 else -1

    mode_name = "PIVOT RIGHT" if pivot == RIGHT else ("PIVOT LEFT" if pivot == LEFT else "TANK")

    print("\n" + "=" * 62)
    print("СТАРТ LQR [{}] | Старт: {:.2f}° -> Цель: {:.2f}° (угол: {:+}°)".format(
        mode_name, start_heading, target_heading, angle
    ))
    print("K1 =", gain_k1, "| K2 =", gain_k2, "| MIN_PWR =", p_min, "| TOL =", tol)
    print("-" * 62)
    print("Время(мс) | Курс(°) | Осталось(°) | Скор.(°/с) | Мощность")
    print("-" * 62)

    if pivot == RIGHT:
        right_drive.hold()
    elif pivot == LEFT:
        left_drive.hold()

    while True:
        current_heading = hub.imu.heading()
        err = wrap_angle(target_heading - current_heading)
        gyro_z = hub.imu.angular_velocity()[2]

        # Фиксируем перелёт (когда робот проскочил цель по инерции)
        overshoot = -err * turn_sign
        if overshoot > max_overshoot:
            max_overshoot = overshoot

        if abs(err) <= tol and abs(gyro_z) < 2.5:
            break

        if timer.time() > timeout_ms:
            print("!!! ВЫХОД ПО ТАЙМАУТУ ({} мс) !!!".format(timeout_ms))
            break

        raw_power = (gain_k1 * err + gain_k2 * gyro_z) * v_scale
        pwr = _clamp(raw_power, -p_max, p_max)

        if abs(err) < 3.0:
            effective_min = max(6.0, p_min * (abs(err) / 3.0))
        else:
            effective_min = p_min

        if abs(pwr) < effective_min:
            pwr = effective_min if err > 0 else -effective_min

        if pivot is None:
            left_drive.dc(pwr)
            right_drive.dc(-pwr)
        elif pivot == RIGHT:
            left_drive.dc(pwr)
        elif pivot == LEFT:
            right_drive.dc(-pwr)

        now = timer.time()
        if now - last_print_ms >= 40:
            last_print_ms = now
            print(
                "{:8d} | {:7.2f} | {:+11.2f} | {:+10.1f} | {:+8.1f}".format(
                    now, current_heading, err, gyro_z, pwr
                )
            )

        wait(5)

    elapsed_ms = timer.time()
    left_drive.hold()
    right_drive.hold()
    wait(180)  # Ждём полной остановки, чтобы замерить реальный финальный угол

    final_heading = hub.imu.heading()
    final_err = wrap_angle(target_heading - final_heading)
    actual_delta = wrap_angle(final_heading - start_heading)

    print("-" * 62)
    print("ИТОГ ПОВОРОТА:")
    print("  Время выполнения      :", elapsed_ms, "мс")
    print("  Повернул по факту     : {:+.2f}° (цель: {:+}°)".format(actual_delta, angle))
    print("  Итоговый курс на поле : {:.2f}° (цель: {:.2f}°)".format(final_heading, target_heading))
    print("  Финальная ошибка      : {:+.2f}°".format(final_err))
    print("  Макс. перелёт инерции : {:.2f}°".format(max_overshoot))
    print("=" * 62 + "\n")


def run_lqr_test():
    """Главная функция тестового рана LQR."""
    print_battery()
    set_heading(0.0)
    print("Начальный курс установлен: {:.2f}°".format(hub.imu.heading()))
    wait(400)

    # 1. Серия танковых поворотов (направо, налево, разворот на 180°)
    for ang in TEST_ANGLES:
        turn_lqr_debug(power=TEST_POWER, angle=ang)
        wait(600)

    # 2. Тест одноколёсных поворотов (если включено TEST_PIVOT = True)
    if TEST_PIVOT:
        turn_lqr_debug(power=TEST_POWER, angle=90, pivot=RIGHT)
        wait(600)
        turn_lqr_debug(power=TEST_POWER, angle=-90, pivot=LEFT)


if __name__ == "__main__":
    run_lqr_test()