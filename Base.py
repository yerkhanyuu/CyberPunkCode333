"""
Base.py — общая точка входа в библиотеку робота команды Heaven.
Объединяет все чистые модули в одном импорте для ранов и меню:
    from Base import *

Доступные основные команды в заездах:
    go(dist_mm, start_speed, max_speed, end_speed, brake_mm, accel_rate)
    turn(power, angle, pivot=None)
    turn_to(power, target_angle, pivot=None)
    lefta(power, deg, wait=True)
    righta(power, deg, wait=True)
    align_wall(power=-35, timeout_ms=1000, reset_angle=0.0)
    set_heading(0.0)
"""

from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.tools import wait, StopWatch, Matrix

from config import *
from robot import *
from driving import *
from turning import *
from attachments import *

# Короткие псевдонимы остановки и поворота для удобства в заездах
bc_stop = stop_all