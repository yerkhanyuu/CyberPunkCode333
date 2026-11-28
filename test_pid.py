"""
test_pid.py — тестовый заезд для калибровки PID-регулятора прямолинейного движения.
Показывает в терминале курс, отклонение (ошибку) в градусах и пройденные миллиметры
в реальном времени, а в конце выводит сводку для быстрой подстройки KP, KI, KD.
"""

from Base import *
from driving import _voltage_scale, _clamp

# ==============================================================================
# 1. КОЭФФИЦИЕНТЫ ДЛЯ ПОДБОРА (Меняй здесь, когда найдёшь идеал — перенеси в config.py)
# ==============================================================================
TEST_KP = DRIVE_KP          # Реакция на отклонение от курса (начни с 1.2 - 1.8)
TEST_KI = DRIVE_KI              # Накопление ошибки (держи 0.0 при первичной настройке)
TEST_KD = DRIVE_KD          # Гашение рыскания / змейки (начни с 0.1 - 0.4)
TEST_ADAPT = DRIVE_ADAPT_GAIN  # Адаптация при наезде на препятствия (0.0 при базовой настройке)

# Параметры тестового проезда
TEST_DIST_MM = 800          # Дистанция теста в мм (+ вперёд, - назад)
TEST_START_SPEED = 15       # Начальная скорость
TEST_MAX_SPEED = 80         # Максимальная скорость
TEST_END_SPEED = 27         # Конечная скорость
TEST_BRAKE_MM = 100         # За сколько мм до финиша начать торможение
TEST_ACCEL = 1.5            # Ускорение
RETURN_BACK = True          # True: после паузы вернуться назад на старт


def go_pid_debug(
    dist_mm,
    start_speed,
    max_speed,
    end_speed,
    brake_mm,
    accel_rate,
    kp,
    ki,
    kd,
    adapt_gain,
):
    """
    Точная копия алгоритма go() из driving.py с выводом телеметрии в терминал
    каждые 50 мс (чтобы не перегружать канал связи хаба).
    """
    drive_base.stop()

    direction = 1 if dist_mm > 0 else -1
    target_deg = abs(mm_to_deg(dist_mm))
    brake_deg = max(0, abs(mm_to_deg(brake_mm)))
    decel_start_deg = max(0, target_deg - brake_deg)

    target_heading = state.heading
    s_start = abs(start_speed)
    s_max = max(s_start, abs(max_speed))
    s_end = abs(end_speed)
    step_accel = abs(accel_rate)
    v_scale = _voltage_scale()

    left_drive.reset_angle(0)
    right_drive.reset_angle(0)

    current_speed = s_start
    peak_reached_speed = s_start
    decel_started = False

    integral = 0.0
    prev_error = wrap_angle(target_heading - hub.imu.heading())

    max_abs_error = 0.0
    oscillations = 0
    last_sign = 0

    timer = StopWatch()
    last_print_ms = 0

    print("\n" + "=" * 54)
    print("СТАРТ ТЕСТА PID | Дистанция:", dist_mm, "мм | Курс:", target_heading)
    print("KP =", kp, "| KI =", ki, "| KD =", kd, "| ADAPT =", adapt_gain)
    print("-" * 54)
    print("Время(мс) | Путь(мм) | Курс(°) | Ошибка(°) | Корр.")
    print("-" * 54)

    while True:
        moved_deg = (abs(left_drive.angle()) + abs(right_drive.angle())) * 0.5
        remaining_deg = target_deg - moved_deg

        if remaining_deg <= 0:
            break

        # Профиль скорости
        if moved_deg >= decel_start_deg and brake_deg > 0:
            if not decel_started:
                decel_started = True
                peak_reached_speed = current_speed
            ratio = remaining_deg / brake_deg
            current_speed = s_end + (peak_reached_speed - s_end) * ratio
        else:
            if current_speed < s_max:
                current_speed = min(s_max, current_speed + step_accel)
            peak_reached_speed = current_speed

        # PID-расчёт
        current_heading = hub.imu.heading()
        error = wrap_angle(target_heading - current_heading)

        if abs(error) > max_abs_error:
            max_abs_error = abs(error)

        # Считаем количество переходов через 0° (индикатор «змейки»)
        if abs(error) > 0.4:
            sign = 1 if error > 0 else -1
            if last_sign != 0 and sign != last_sign:
                oscillations += 1
            last_sign = sign

        if abs(error) < 15.0:
            integral = _clamp(integral + error * 0.005, -20.0, 20.0)
        else:
            integral = 0.0

        derivative = error - prev_error
        prev_error = error

        adaptive_kp = kp * (1.0 + adapt_gain * abs(error))
        correction = (adaptive_kp * error) + (ki * integral) + (kd * derivative)
        correction = _clamp(correction, -DRIVE_MAX_CORRECTION, DRIVE_MAX_CORRECTION)

        base_power = direction * current_speed * v_scale
        left_drive.dc(_clamp(base_power + correction, -100.0, 100.0))
        right_drive.dc(_clamp(base_power - correction, -100.0, 100.0))

        # Печатаем в терминал раз в 50 мс
        now = timer.time()
        if now - last_print_ms >= 50:
            last_print_ms = now
            moved_mm = int((moved_deg / 360.0) * 3.14159 * TIRE_DIAMETER) * direction
            print(
                "{:8d} | {:8d} | {:7.2f} | {:+9.2f} | {:+6.1f}".format(
                    now, moved_mm, current_heading, error, correction
                )
            )

        wait(5)

    left_drive.hold()
    right_drive.hold()
    wait(150)

    final_heading = hub.imu.heading()
    final_error = wrap_angle(target_heading - final_heading)
    final_mm = int(((abs(left_drive.angle()) + abs(right_drive.angle())) * 0.5 / 360.0) * 3.14159 * TIRE_DIAMETER) * direction

    print("-" * 54)
    print("ИТОГ ПРОЕЗДА:")
    print("  Пройдено по энкодерам :", final_mm, "мм (цель:", dist_mm, "мм)")
    print("  Макс. отклонение курса:", round(max_abs_error, 2), "°")
    print("  Финальная ошибка курса:", round(final_error, 2), "°")
    print("  Колебаний («змейка»)  :", oscillations)
    print("=" * 54 + "\n")


def run_pid_test():
    """Главная функция тестового рана PID."""
    print_battery()
    set_heading(0.0)

    # Проезд вперёд с выводом отклонений
    go_pid_debug(
        dist_mm=TEST_DIST_MM,
        start_speed=TEST_START_SPEED,
        max_speed=TEST_MAX_SPEED,
        end_speed=TEST_END_SPEED,
        brake_mm=TEST_BRAKE_MM,
        accel_rate=TEST_ACCEL,
        kp=TEST_KP,
        ki=TEST_KI,
        kd=TEST_KD,
        adapt_gain=TEST_ADAPT,
    )

    if RETURN_BACK:
        wait(600)
        # Обратный проезд на тот же курс 0.0°, чтобы проверить движение задом
        go_pid_debug(
            dist_mm=-TEST_DIST_MM,
            start_speed=TEST_START_SPEED,
            max_speed=TEST_MAX_SPEED,
            end_speed=TEST_END_SPEED,
            brake_mm=TEST_BRAKE_MM,
            accel_rate=TEST_ACCEL,
            kp=TEST_KP,
            ki=TEST_KI,
            kd=TEST_KD,
            adapt_gain=TEST_ADAPT,
        )


if __name__ == "__main__":
    run_pid_test()