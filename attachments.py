"""
attachments.py — модуль управления насадками команды Heaven.
Содержит:
1. Точные команды lefta / righta на встроенном контроллере Pybricks (run_angle).
2. Силовые ударные команды lefta_dc / righta_dc через прямое напряжение (.dc())
   для максимального крутящего момента без программного ограничения скорости.

Во всех функциях положительный угол (+deg) поднимает насадку ВВЕРХ,
а отрицательный (-deg) опускает ВНИЗ.
"""

from pybricks.parameters import Stop
from pybricks.tools import wait, StopWatch
from config import ATT_SPEED_SCALE
from robot import left_att_motor, right_att_motor


def _calc_speed(power):
    """Переводит мощность (1..100) в скорость (град/с), всегда положительную."""
    p = max(1, min(100, abs(power)))
    return p * ATT_SPEED_SCALE


def _clamp_power(power):
    """Ограничивает мощность в безопасном диапазоне [1, 100]."""
    return max(1, min(100, abs(power)))


def lefta(power, deg, wait=True, then=Stop.HOLD):
    """
    Поворачивает левую насадку на заданный угол с заданной мощностью (PID Pybricks).

    Примеры:
        lefta(90, 100)              # Поднять на 100° вверх с мощностью 90
        lefta(80, -120)             # Опустить на 120° вниз с мощностью 80
        lefta(100, 180, wait=False) # Запустить в фоне во время езды
    """
    if deg == 0:
        return
    left_att_motor.run_angle(_calc_speed(power), deg, then=then, wait=wait)


def righta(power, deg, wait=True, then=Stop.HOLD):
    """
    Поворачивает правую насадку на заданный угол с заданной мощностью (PID Pybricks).

    Примеры:
        righta(90, 100)              # Поднять на 100° вверх с мощностью 90
        righta(80, -120)             # Опустить на 120° вниз с мощностью 80
        righta(100, 180, wait=False) # Запустить в фоне во время езды
    """
    if deg == 0:
        return
    right_att_motor.run_angle(_calc_speed(power), deg, then=then, wait=wait)


def _att_dc_core(motor, power, deg, timeout_ms=1500, hold=True):
    """
    Внутреннее ядро прямого силового тока (.dc()) для максимального крутящего момента.
    Направление задаётся знаком deg (+ вверх, - вниз), мощность всегда 1..100.
    """
    if deg == 0:
        return

    target_deg = abs(deg)
    direction = 1 if deg > 0 else -1
    dc_cmd = direction * _clamp_power(power)

    motor.reset_angle(0)
    timer = StopWatch()

    while abs(motor.angle()) < target_deg:
        if timer.time() > timeout_ms:
            print("ТАЙМАУТ насадки DC на угле:", motor.angle(), "/", deg)
            break
        motor.dc(dc_cmd)
        wait(2)

    if hold:
        motor.hold()
    else:
        motor.dc(0)


def lefta_dc(power, deg, timeout_ms=1500, hold=True):
    """
    Максимально сильный и быстрый удар/поворот левой насадкой напрямую через .dc().

    Примеры:
        lefta_dc(100, 90)    # Резкий подъём на 90° вверх на 100% тока батареи
        lefta_dc(100, -120)  # Резкий удар на 120° вниз на 100% тока батареи
    """
    _att_dc_core(left_att_motor, power, deg, timeout_ms=timeout_ms, hold=hold)


def righta_dc(power, deg, timeout_ms=1500, hold=True):
    """
    Максимально сильный и быстрый удар/поворот правой насадкой напрямую через .dc().

    Примеры:
        righta_dc(100, 90)   # Резкий подъём на 90° вверх на 100% тока батареи
        righta_dc(100, -120) # Резкий удар на 120° вниз на 100% тока батареи
    """
    _att_dc_core(right_att_motor, power, deg, timeout_ms=timeout_ms, hold=hold)


# Короткие псевдонимы на случай использования старых имён в заездах
left_att_dc = lefta_dc
right_att_dc = righta_dc


def stop_attachments():
    """Снимает удержание и обесточивает оба мотора насадок."""
    left_att_motor.dc(0)
    right_att_motor.dc(0)