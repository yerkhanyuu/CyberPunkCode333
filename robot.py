"""
robot.py — инициализация хаба, моторов, DriveBase (без гироскопа)
и управление абсолютным курсом команды Heaven.
"""

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait
from umath import pi

from config import (
    TIRE_DIAMETER,
    AXLE_TRACK,
    STOP_BUTTON,
    LEFT_DRIVE_PORT,
    LEFT_DRIVE_DIR,
    RIGHT_DRIVE_PORT,
    RIGHT_DRIVE_DIR,
    LEFT_ATT_PORT,
    LEFT_ATT_DIR,
    RIGHT_ATT_PORT,
    RIGHT_ATT_DIR,
)

# ==============================================================================
# 1. ИНИЦИАЛИЗАЦИЯ ХАБА И МОТОРОВ
# ==============================================================================
hub = PrimeHub()
hub.system.set_stop_button(STOP_BUTTON)

# Приводные моторы
left_drive = Motor(LEFT_DRIVE_PORT, LEFT_DRIVE_DIR)
right_drive = Motor(RIGHT_DRIVE_PORT, RIGHT_DRIVE_DIR)

# Моторы насадок (+deg = вверх, -deg = вниз)
left_att_motor = Motor(LEFT_ATT_PORT, LEFT_ATT_DIR)
right_att_motor = Motor(RIGHT_ATT_PORT, RIGHT_ATT_DIR)

# DriveBase с отключённым встроенным гироскопом (чтобы не мешал нашим PID и LQR)
drive_base = DriveBase(
    left_drive,
    right_drive,
    wheel_diameter=TIRE_DIAMETER,
    axle_track=AXLE_TRACK,
)
drive_base.use_gyro(False)


# ==============================================================================
# 2. СОСТОЯНИЕ АБСОЛЮТНОГО КУРСА
# ==============================================================================
class _RobotState:
    def __init__(self):
        self.heading = 0.0


state = _RobotState()


# ==============================================================================
# 3. УТИЛИТЫ КУРСА, ГЕОМЕТРИИ И БЕЗОПАСНОЙ ОСТАНОВКИ
# ==============================================================================
def wrap_angle(angle):
    """Нормализует любой угол в диапазон [-180.0, 180.0] градусов."""
    return (angle + 180.0) % 360.0 - 180.0


def mm_to_deg(mm, wheel_diameter=TIRE_DIAMETER):
    """Переводит расстояние в миллиметрах в градусы поворота колеса."""
    return (mm / (pi * wheel_diameter)) * 360.0


def set_heading(angle=0.0):
    """Жёстко устанавливает текущий курс гироскопа и целевой курс (например, на старте)."""
    left_drive.dc(0)
    right_drive.dc(0)
    hub.imu.reset_heading(angle)
    state.heading = float(angle)
    wait(60)


def sync_heading():
    """Синхронизирует целевой курс с текущим реальным положением гироскопа."""
    state.heading = float(hub.imu.heading())


def stop_all():
    """Экстренно обесточивает все моторы шасси и насадок."""
    drive_base.stop()
    left_drive.dc(0)
    right_drive.dc(0)
    left_att_motor.dc(0)
    right_att_motor.dc(0)


def print_battery():
    """Выводит напряжение батареи в консоль для контроля перед заездом."""
    mv = hub.battery.voltage()
    print("Battery:", mv, "mV (", round(mv / 1000.0, 2), "V )")