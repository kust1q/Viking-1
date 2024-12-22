import krpc
import time
import math
import threading
import log

conn = krpc.connect()  # подключаемся к серверу
vessel = conn.space_center.active_vessel  # активный корабль
control = vessel.control  # контролировать корабль
ap = vessel.auto_pilot  # работать с автопилотом

# Подготовка к запуску
ap.target_pitch_and_heading(90, 90)
ap.engage()

# Переменные потоки, при которых мы получаем данные из KSP
ut = conn.add_stream(getattr, conn.space_center, 'ut')  # текущее время в KSP
stage_6_resources = vessel.resources_in_decouple_stage(stage=6, cumulative=False)  # пятая ступень
srb_fuel = conn.add_stream(stage_6_resources.amount, 'SolidFuel')  # количество топлива во всех ускорителях
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')  # высота над уровнем моря
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')  # высота апоцентра
speed = conn.add_stream(getattr, vessel.flight(vessel.orbit.body.reference_frame), "speed") # скорость
angle = conn.add_stream(getattr, vessel.auto_pilot, "target_pitch") # угол наклона
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')  # высота перицентра
pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')  # угол рысканья ракеты

# Параметры, с которыми ракета будет наклоняться (высота апоцентра, угол рысканья)
pos0, pos1 = (18500, 0), (58500, math.pi / 2)  # измените значения в соответствии с параметрами ракеты

def set_elliptic(pos0, pos1):
    p, q = pos0
    s, r = pos1
    a = s - p
    b = r - q
    
    def func(x):
        if x < pos0[0] or x > pos1[0]:
            return pos0[1] if x < pos0[0] else pos1[1]
        return math.sqrt(b ** 2 - (b / a) ** 2 * (x - s) ** 2) + q

    return func

# Функция угла наклона ракеты
angle = set_elliptic(pos0, pos1)


log_file = log.create_log_file()
log_thread = threading.Thread(target=log.collect_data_and_log, args=(conn, vessel, log_file,))
log_thread.start()

# ВЗЛЁТ РАКЕТЫ (доорбитальный этап)
print("3...")
time.sleep(0.5)
print("2...")
time.sleep(0.5)
print("1...")
time.sleep(0.5)

print("Start!")
control.activate_next_stage()
vessel.control.throttle = 0.2
start_time_flight = ut()

# Ждем, пока апоцентр достигнет нужной высоты
while altitude() < pos0[0]:
   time.sleep(0.5)

# Наклоняем ракету до тех пор, пока топливо в ускорителях не закончится
while srb_fuel() > 1500:
    ap.target_pitch = math.degrees(math.pi / 2 - angle(altitude()))
    print(srb_fuel(), math.degrees(math.pi / 2 - angle(altitude())))
    time.sleep(0.2)

# Устанавливаем угол наклона 0 после того, как топливо в ускорителях почти закончится
ap.target_pitch = 0

# Отсоединяем ускорители
vessel.control.throttle = 0.2
control.activate_next_stage()
print("Ускорители отброшены")

# ВЫХОД НА КРУГОВУЮ ОРБИТУ (орбитальный этап)

# Функция, которая считает гомановский переход
def test3(mu, r1, r2):
    a = (r1 + r2) / 2
    dv1 = math.sqrt(mu / r1) * (math.sqrt(r2 / a) - 1)
    dv2 = math.sqrt(mu / r2) * (1 - math.sqrt(r1 / a))
    return dv1, dv2

# Ждем немного, чтобы всё стабилизировалось
time.sleep(1)

# Расчет и создание маневра
print("Добавляем ноду манёвра")
mu = vessel.orbit.body.gravitational_parameter
delta_v = test3(mu, vessel.orbit.periapsis, vessel.orbit.apoapsis)[1]
node = control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)
vessel.control.throttle = 0.2
time.sleep(7)
vessel.control.throttle = 0
# Рассчитываем время работы двигателя
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate


print("Выключаем автопилот")
ap.disengage()
print("Включаем САС")
control.sas = True
time.sleep(0.5)
print("Ставим САС на манёвр")
control.sas_mode = conn.space_center.SASMode.maneuver

# Ждем момента маневра
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2)
lead_time = 5
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, "time_to_apoapsis")

while time_to_apoapsis() - (burn_time / 2) > 0:
    time.sleep(0.05)

# Запускаем двигатели
print("Запускаем двигатели", altitude(), speed())


#control.throttle = 0.80773
control.throttle = 1
# time_when_end = ut() + vessel.orbit.time_to_apoapsis + (burn_time / 2)
# # time.sleep(20)
# while time_when_end - ut() > 0:
#     time.sleep(0.05)


#vessel.orbit.apoapsis_altitude < 100000 and
while  vessel.orbit.apoapsis_altitude < 108000 and vessel.orbit.periapsis_altitude < 94000 :
    pass
print(vessel.orbit.apoapsis_altitude, vessel.orbit.periapsis_altitude)


# Завершаем маневр
print("Ракета успешно выведена на орбиту 100 км")
log.stop_logging()
end_time_flight = ut()
print("Время полёта", end_time_flight - start_time_flight)
print("Скорость", speed())
control.throttle = 0
time.sleep(20)
control.activate_next_stage()
control.remove_nodes()
