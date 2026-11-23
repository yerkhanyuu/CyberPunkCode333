"""
turning.py — модуль высокоточных поворотов команды Heaven на основе LQR-регулятора.
Поддерживает танковый разворот на месте и одноколесный (пивотный) поворот
с сохранением целевого абсолютного курса без накопления ошибок.
"""

from pybricks.tools import wait, StopWatch
from config import (
    LEFT,
    RIGHT,
    TURN_K1,
    TURN_K2,
    TURN_MIN_POWER,
    TURN_TOLERANCE,
    PIVOT_K1,
    PIVOT_K2,
    PIVOT_MIN_POWER,
    PIVOT_TOLERANCE,
    NOMINAL_VOLTAGE_MV,
)
from robot import (
    hub,
    left_drive,
    right_drive,
    drive_base,
    state,
    wrap_angle,
)


def _voltage_scale():
    """Компенсация просадки напряжения батареи для стабильности углов."""
    voltage = hub.battery.voltage()
    if voltage <= 0:
        return 1.0
    scale = NOMINAL_VOLTAGE_MV / voltage
    return max(0.92, min(1.12, scale))


def _clamp(val, min_val, max_val):
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val


def _lqr_turn_core(
    target_heading,
    max_power=80,
    pivot=None,
    k1=None,
    k2=None,
    min_power=None,
    tolerance=None,
    timeout_ms=1500,
):
    """
    Внутреннее ядро LQR-поворота к целевому абсолютному курсу target_heading.
    """
    drive_base.stop()

    is_pivot = pivot in (LEFT, RIGHT)
    gain_k1 = k1 if k1 is not None else (PIVOT_K1 if is_pivot else TURN_K1)
    gain_k2 = k2 if k2 is not None else (PIVOT_K2 if is_pivot else TURN_K2)
    p_min = min_power if min_power is not None else (PIVOT_MIN_POWER if is_pivot else TURN_MIN_POWER)
    tol = tolerance if tolerance is not None else (PIVOT_TOLERANCE if is_pivot else TURN_TOLERANCE)
    p_max = abs(max_power)

    v_scale = _voltage_scale()
    timer = StopWatch()

    # Удерживаем неподвижное колесо при пивотном повороте
    if pivot == RIGHT:
        right_drive.hold()
    elif pivot == LEFT:
        left_drive.hold()

    while True:
        current_heading = hub.imu.heading()
        err = wrap_angle(target_heading - current_heading)

        # Угловая скорость по оси Z (в Pybricks знак противоположен росту heading,
        # поэтому + gain_k2 * gyro_z работает как демпфер инерции)
        gyro_z = hub.imu.angular_velocity()[2]

        # Завершаем поворот, когда попали в допуск и корпус погасил инерцию
        if abs(err) <= tol and abs(gyro_z) < 2.5:
            break

        if timer.time() > timeout_ms:
            break

        raw_power = (gain_k1 * err + gain_k2 * gyro_z) * v_scale
        power = _clamp(raw_power, -p_max, p_max)

        # Плавное снижение минимальной мощности вблизи цели, чтобы не дёргаться
        if abs(err) < 3.0:
            effective_min = max(6.0, p_min * (abs(err) / 3.0))
        else:
            effective_min = p_min

        if abs(power) < effective_min:
            power = effective_min if err > 0 else -effective_min

        if pivot is None:
            # Танковый разворот вокруг центра оси
            left_drive.dc(power)
            right_drive.dc(-power)
        elif pivot == RIGHT:
            # Поворот вокруг правого колеса (крутит левое)
            left_drive.dc(power)
        elif pivot == LEFT:
            # Поворот вокруг левого колеса (крутит правое)
            right_drive.dc(-power)

        wait(5)

    left_drive.hold()
    right_drive.hold()
    wait(40)


def turn(
    power,
    angle,
    pivot=None,
    k1=None,
    k2=None,
    tolerance=None,
    timeout_ms=1500,
):
    """
    Поворот робота на относительный угол на LQR-регуляторе.

    Примеры вызова:
        turn(90, 90)               # Танковый поворот на 90° вправо с мощностью 90
        turn(80, -45)              # Танковый поворот на 45° влево с мощностью 80
        turn(90, 90, pivot=RIGHT)  # Поворот на 90° вокруг правого колеса
        turn(90, -60, pivot=LEFT)  # Поворот на 60° вокруг левого колеса

    Параметры:
        power      — максимальная мощность моторов (1..100)
        angle      — угол поворота в градусах (+ вправо, - влево)
        pivot      — None (танковый), RIGHT (вокруг правого), LEFT (вокруг левого)
        k1, k2     — индивидуальные LQR-коэффициенты (None = из config.py)
        tolerance  — допуск остановки в градусах
        timeout_ms — страховка по времени в миллисекундах
    """
    if angle == 0:
        return

    # Считаем от целевого курса state.heading, чтобы ошибки не накапливались
    state.heading = wrap_angle(state.heading + float(angle))
    _lqr_turn_core(
        target_heading=state.heading,
        max_power=power,
        pivot=pivot,
        k1=k1,
        k2=k2,
        tolerance=tolerance,
        timeout_ms=timeout_ms,
    )


def turn_to(
    power,
    target_angle,
    pivot=None,
    k1=None,
    k2=None,
    tolerance=None,
    timeout_ms=1500,
):
    """
    Поворот на абсолютный курс поля (относительно старта заезда) по кратчайшему пути.

    Пример:
        turn_to(85, 0)    # Вернуться строго на стартовый курс 0°
        turn_to(85, 90)   # Встать строго на курс 90°
    """
    state.heading = wrap_angle(float(target_angle))
    _lqr_turn_core(
        target_heading=state.heading,
        max_power=power,
        pivot=pivot,
        k1=k1,
        k2=k2,
        tolerance=tolerance,
        timeout_ms=timeout_ms,
    )