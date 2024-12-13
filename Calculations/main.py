from math import pi, atan
from Angle_Functions import Linear, Parabolic, Elliptic
import Create_Rocket
import Main_Models
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

thrust_vac = 4_900_000
thrust_ground = 4_409_000
mass_start = 198_472  # 78 472
mass_end = 39_200
fuel_consumption = 200.99
full_fuel = 16000
resis_coefs = [
    *[(0.09, 0.2)] * 3,
    (0.3, 0.1),
    (0.5, 0.2),
    (3, 0.2),
    (0.2, 0.1),
    *[(70, 0.25)] * 2,
    (6, 0.2),
]  # детали (масса в тоннах, кэф сопротивления)

params = (
    thrust_vac,
    thrust_ground,
    mass_start,
    mass_end,
    resis_coefs,
    fuel_consumption,
    full_fuel,
)


def experimennts(function):
    optimal_elliptic = [([], []), ([], []), 10**10]
    for lower in range(8000, 30001, 1500):
        for higher in range(30000, 60001, 1500):
            our_func = function((lower, 0), (higher, pi / 2))
            Viking_first = Create_Rocket.Rocket(our_func)
            Viking_first.add_stage(stage=Create_Rocket.Stage(*params))

            traectory, orbit, delta_v = Main_Models.FlightModel(
                Viking_first,
                Viking_first.stages[0],
                Viking_first.stages[0].max_time_moving,
            )
            if delta_v < optimal_elliptic[2]:
                optimal_elliptic[0] = traectory
                optimal_elliptic[1] = orbit
                optimal_elliptic[2] = delta_v

    print("Необходимый delta_v", optimal_elliptic[2])
    print("График изменения угла от координаты X")
    X_angle_takeof = [0]
    Y_angle_takeof = [0]
    angles = []
    for i in range(len(optimal_elliptic[0][0]) - 1):
        if i == len(optimal_elliptic[0][0]) - 2:
            X_angle_takeof.append(
                optimal_elliptic[1][0][0] - optimal_elliptic[0][0][i + 1]
            )
        X_angle_takeof.append(optimal_elliptic[0][0][i + 1] - optimal_elliptic[0][0][i])

    for i in range(len(optimal_elliptic[0][1]) - 1):
        if i == len(optimal_elliptic[0][1]) - 2:
            Y_angle_takeof.append(
                optimal_elliptic[1][1][0] - optimal_elliptic[0][1][i + 1]
            )
        Y_angle_takeof.append(optimal_elliptic[0][1][i + 1] - optimal_elliptic[0][1][i])

    for i in range(1, len(X_angle_takeof)):
        if X_angle_takeof[i] == 0.0:
            angles.append(pi / 2)
            continue
        angles.append(atan(Y_angle_takeof[i] / X_angle_takeof[i]))

    X_angle_orbit = [optimal_elliptic[0][0][-1]]
    Y_angle_orbit = [optimal_elliptic[1][0][-1]]
    angles_orbit = [angles[-1]]
    for i in range(len(optimal_elliptic[1][0]) - 1):
        X_angle_orbit.append(optimal_elliptic[1][0][i + 1] - optimal_elliptic[1][0][i])

    for i in range(len(optimal_elliptic[1][1]) - 1):
        Y_angle_orbit.append(optimal_elliptic[1][1][i + 1] - optimal_elliptic[1][1][i])

    for i in range(1, len(X_angle_orbit)):
        if X_angle_orbit[i] == 0.0:
            angles_orbit.append(pi / 2)
            continue
        angles_orbit.append(atan(Y_angle_orbit[i] / X_angle_orbit[i]))

    plt.plot(optimal_elliptic[0][0], angles)
    plt.plot(optimal_elliptic[1][0], angles_orbit)
    plt.show()

    print("График траектории ракеты")
    figure(figsize=(10, 10))
    kerbin_orbit = Main_Models.DrawKerbinOrbit()
    plt.plot(*kerbin_orbit)
    plt.plot(*optimal_elliptic[0])
    plt.plot(*optimal_elliptic[1])
    plt.gca().set_aspect("equal", adjustable="box")
    plt.show()


print("Линейный закон")
experimennts(Linear)
print("Параболический закон")
experimennts(Parabolic)
print("Эллиптический закон")
experimennts(Elliptic)
