import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Константы ракеты
F_thrust = 3700e3  # Тяга в вакууме (Н)
Isp = 235  # Удельный импульс (с)
g = 9.81  # Ускорение свободного падения (м/с^2)
m_start = 198471.609375  # Начальная масса ракеты (кг)
m_end = 82661.640625  # Конечная масса ракеты (кг)
altitude = 31953.13868602353  # Высота взлета (м)
A = 3.14 * (2 * 2.5 ** 2 + 2.75 ** 2)  # Площадь поперечного сечения (м^2)
Cd = 0.2  # Коэффициент сопротивления формы

# Параметры эллипса для изменения угла
p, q = 19000, np.radians(90)  # Точка 1: Высота начала изменения угла, угол (радианы)
s, r = altitude, np.radians(23.01616859436035)  # Точка 2: Высота взлета, угол

a = s - p  # Большая полуось
b = r - q  # Малая полуось

# Функция изменения угла
def theta_func(h):
    if h <= p:  # До апоцентра угол фиксирован
        return q
    elif h <= s:  # После апоцентра изменяется по эллиптической формуле
        return np.radians(180) - (np.sqrt(b**2 - (b / a)**2 * (h - s)**2) + q)
    else:  # На высоте больше орбиты угол фиксируется
        return r

# Уравнения движения ракеты
def equations(t, y):
    vx, vy, h = y
    
    theta = theta_func(h)  # Угол зависит от высоты
    ph = 1 * np.exp(-h / 5000) # Атмосферное давление в зависимости от высоты
    rho = 1.2230948554874 * ph  # Плотность воздуха (экспоненциальное убывание)
    F_dynamic_thrust = 3700e3 - (3700e3 - 3300e3) * ph # Изменение тяги в зависимости от высоты
    global mdot
    mdot = F_dynamic_thrust / (Isp * g)
    m = m_start - mdot * t  # Масса ракеты уменьшается до минимальной
    v = np.sqrt(vx**2 + vy**2) # Скорость ракеты
    drag = 0.5 * Cd * A * rho * v**2 # Сила сопротивления
    #дифференциальные уравнения
    dvx_dt = (F_dynamic_thrust * np.cos(theta) - drag * np.cos(theta)) / m 
    dvy_dt = (F_dynamic_thrust * np.sin(theta) - (drag * np.sin(theta) + m * g)) / m
    dh_dt = vy  

    return [dvx_dt, dvy_dt, dh_dt]
    
# Начальные условия
y0 = [0, 0, 18]  # [vx, vy, h]

# Решение системы
t_max = 74 # Максимальное время моделирования
time = np.linspace(0, t_max, 1000)
solution = solve_ivp(equations, [0, t_max], y0, t_eval=time)
vx = solution.y[0]
vy = solution.y[1]
h = solution.y[2]
v = np.sqrt(vx**2 + vy**2)
theta_deg = np.degrees([theta_func(hi) for hi in h])
mass = np.maximum(m_end, m_start - mdot * time)  # Масса ракеты

# Чтение данных из файла
time_file = []
mass_file = []
speed_file = []
angle_file = []
altitude_file = []

with open("data.json", encoding="UTF-8") as file:
    for line in file:
        line = json.loads(line.strip())
        time_file.append(float(line["time"]))
        mass_file.append(float(line["mass"]))
        speed_file.append(float(line["speed"]))
        angle_file.append(float(line["angle"]))
        altitude_file.append(float(line["altitude"]))


# Построение графиков
plt.figure(figsize=(12, 16))

# График скорости
plt.subplot(4, 1, 1)
plt.plot(time, v, label="Speed (model)", color="red")
plt.plot(time_file, speed_file, label="Speed (logger)", linestyle="--", color="orange")
plt.title("Скорость ракеты от времени")
plt.xlabel("Time (s)")
plt.ylabel("Speed (m/s)")
plt.grid()
plt.legend()

# График высоты
plt.subplot(4, 1, 2)
plt.plot(time, h, label="Altitude (model)", color="blue")
plt.plot(time_file, altitude_file, label="Altitude (logger)", linestyle="--", color="cornflowerblue")
plt.title("Высота ракеты от времени")
plt.xlabel("Time (s)")
plt.ylabel("Altitude (m)")
plt.grid()
plt.legend()

# График угла
plt.subplot(4, 1, 3)
plt.plot(time, theta_deg, label="Angle (model)", color="indigo")
plt.plot(time_file, angle_file, label="Angle (logger)", linestyle="--", color="violet")
plt.title("Угол наклона ракеты от времени")
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.grid()
plt.legend()

# График массы
plt.subplot(4, 1, 4)
plt.plot(time, mass, label="Mass (model)", color="green")
plt.plot(time_file, mass_file, label="Mass (logger)", linestyle="--", color="limegreen")
plt.title("Масса ракеты от времени")
plt.xlabel("Time (s)")
plt.ylabel("Mass (kg)")
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()

