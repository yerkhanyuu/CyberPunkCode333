"""
driving.py — модуль высокоточного прямолинейного движения команды Heaven.
Работает напрямую через напряжение моторов (.dc()) и встроенный IMU хаба
без использования DriveBase.use_gyro и датчиков цвета.
"""

from pybricks.tools import wait, StopWatch
from config import (
    DRIVE_KP,
    DRIVE_KI,
    DRIVE_KD,
    DRIVE_ADAPT_GAIN,
    DRIVE_MAX_CORRECTION,
    NOMINAL_VOLTAGE_MV,
    STALL_TIMEOUT_MS,
    STALL_SPEED_DEG_S,
    STALL_GRACE_MS,
)
from robot import (
    hub,
    left_drive,
    right_drive,
    drive_base,
    state,
    mm_to_deg,
    wrap_angle,
)


def _voltage_scale():
    """
    Коэффициент компенсации заряда батареи.
    Позволяет роботу ехать одинаково стабильно при 8.3 В и при 7.8 В.
    """
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


def go(
    dist_mm,
    start_speed=20,
    max_speed=80,
    end_speed=20,
    brake_mm=80,
    accel_rate=2.0,
    heading=None,
    kp=DRIVE_KP,
    ki=DRIVE_KI,
    kd=DRIVE_KD,
    brake=True,
    stall_stop=True,
    timeout_ms=None,
):
    """
    Плавное прямолинейное движение вперёд или назад с адаптивным PID по курсу.

    Пример вызова:
        go(500, 10, 80, 50, 100, 1)
        go(-300, 15, 70, 20, 80, 1.5)

    Параметры:
        dist_mm     — дистанция в мм (+ вперёд, - назад)
        start_speed — стартовая мощность (1..100)
        max_speed   — максимальная маршевая мощность (1..100)
        end_speed   — конечная мощность перед остановкой (1..100)
        brake_mm    — за сколько мм до цели начинать плавное торможение
        accel_rate  — шаг набора мощности за один цикл (5 мс)
        heading     — целевой курс в градусах (None = текущий абсолютный курс)
        kp, ki, kd  — коэффициенты PID-регулятора курса
        brake       — True: удержать моторы в конце (.hold()), False: плавный переход
        stall_stop  — защита от заклинивания при упоре в препятствие
        timeout_ms  — максимальное время выполнения (None = авторасчёт)
    """
    if dist_mm == 0:
        return

    # Освобождаем DriveBase перед прямым управлением через .dc()
    drive_base.stop()

    direction = 1 if dist_mm > 0 else -1
    target_deg = abs(mm_to_deg(dist_mm))
    brake_deg = max(0, abs(mm_to_deg(brake_mm)))
    decel_start_deg = max(0, target_deg - brake_deg)

    if heading is not None:
        state.heading = float(heading)
    target_heading = state.heading

    # Нормализация скоростей
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

    timer = StopWatch()
    last_move_ms = 0
    if timeout_ms is None:
        # Автоматический безопасный таймаут с запасом
        timeout_ms = int(abs(dist_mm) * 8 + 1500)

    while True:
        # Пройденный путь по среднему значению обоих энкодеров (точнее, чем по одному колесу)
        moved_deg = (abs(left_drive.angle()) + abs(right_drive.angle())) * 0.5
        remaining_deg = target_deg - moved_deg

        if remaining_deg <= 0:
            break

        if timer.time() > timeout_ms:
            break

        # 1. Трапецеидальный профиль скорости без скачков на коротких дистанциях
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

        # 2. Адаптивный PID-регулятор удержания курса
        error = wrap_angle(target_heading - hub.imu.heading())

        # Интегральная часть с защитой от насыщения (anti-windup)
        if abs(error) < 15.0:
            integral = _clamp(integral + error * 0.005, -20.0, 20.0)
        else:
            integral = 0.0

        derivative = error - prev_error
        prev_error = error

        # Адаптация: если робот наехал на стык/препятствие (ошибка > 2°),
        # усиливаем реакцию пропорционально отклонению для быстрого возврата на траекторию
        adaptive_kp = kp * (1.0 + DRIVE_ADAPT_GAIN * abs(error))

        correction = (adaptive_kp * error) + (ki * integral) + (kd * derivative)
        correction = _clamp(correction, -DRIVE_MAX_CORRECTION, DRIVE_MAX_CORRECTION)

        # 3. Расчёт итоговой мощности с учётом направления и заряда батареи
        base_power = direction * current_speed * v_scale
        left_power = _clamp(base_power + correction, -100.0, 100.0)
        right_power = _clamp(base_power - correction, -100.0, 100.0)

        left_drive.dc(left_power)
        right_drive.dc(right_power)

        # 4. Защита от заклинивания (игнорирует первые STALL_GRACE_MS на плавном старте)
        if stall_stop:
            now = timer.time()
            avg_wheel_speed = (abs(left_drive.speed()) + abs(right_drive.speed())) * 0.5
            if avg_wheel_speed > STALL_SPEED_DEG_S:
                last_move_ms = now
            elif now > STALL_GRACE_MS and (now - last_move_ms) > STALL_TIMEOUT_MS:
                break

        wait(5)

    if brake:
        left_drive.hold()
        right_drive.hold()
        wait(30)
    else:
        left_drive.dc(0)
        right_drive.dc(0)


def align_wall(power=-35, timeout_ms=1000, reset_angle=0.0):
    """
    Выравнивание задом или передом о борт поля по реальной остановке моторов
    с фиксацией нового абсолютного курса.
    """
    drive_base.stop()
    safe_power = _clamp(power, -100, 100)

    left_drive.dc(safe_power)
    right_drive.dc(safe_power)
    wait(150)  # Даём моторам тронуться

    timer = StopWatch()
    while timer.time() < timeout_ms:
        if abs(left_drive.speed()) < 15 and abs(right_drive.speed()) < 15:
            break
        wait(10)

    left_drive.dc(0)
    right_drive.dc(0)
    wait(60)

    hub.imu.reset_heading(reset_angle)
    state.heading = float(reset_angle)
    wait(40)
```

### Что сделано в `driving.py`:
* **Твоя сигнатура `go(dist_mm, start_speed, max_speed, end_speed, brake_mm, accel_rate)`**: полностью соответствует твоему примеру `go(500, 10, 80, 50, 100, 1)` и автоматически поддерживает движение назад при отрицательном `dist_mm`.
* **Адаптивный PID + защита от скачков**: при наезде на препятствие `adaptive_kp` мягко усиливает коррекцию и возвращает робота на линию; при торможении расчёт идёт от реально достигнутой скорости (`peak_reached_speed`), поэтому на коротких дистанциях робот не «прыгает» вперёд.
* **Стабильность при 7.8–8.3 В**: `_voltage_scale()` автоматически подстраивает мощность под текущий заряд батареи, а средний путь берётся по обоим энкодерам.