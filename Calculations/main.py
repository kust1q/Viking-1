from math import pi
from Angle_Functions import Linear, Parabolic, Elliptic
import Create_Rocket
import Main_Models
import matplotlib.pyplot as plt


thrust_vac = 4_900_000
thrust_ground = 4_409_000
mass_start = 198_472  # 78 472
mass_end = 15_700
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
    optimal_elliptic = [(0, 0), ([], []), ([], []), 10**10]
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
            if delta_v < optimal_elliptic[3]:
                optimal_elliptic[0] = (lower, higher)
                optimal_elliptic[1] = traectory
                optimal_elliptic[2] = orbit
                optimal_elliptic[3] = delta_v

    print("Необходимый delta_v", optimal_elliptic[3])
    print(optimal_elliptic[0])

    kerbin_orbit = Main_Models.DrawKerbinOrbit()
    plt.plot(*kerbin_orbit)
    plt.plot(*optimal_elliptic[1])
    plt.plot(*optimal_elliptic[2])
    plt.gca().set_aspect("equal", adjustable="box")
    plt.show()


print("Линейный закон")
experimennts(Linear)
print("Параболический закон")
experimennts(Parabolic)
print("Эллиптический закон")
experimennts(Elliptic)
