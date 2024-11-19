from math import sqrt, pi, sin, cos
import Constants
import Create_Rocket
import Physics


def KerbinOrbitFlightSimulation(rocket=Create_Rocket.Rocket()):
    position = rocket.position
    velocity = rocket.velocity
    mass = rocket.last_curr_mass()
    resis_coef = rocket.curr_resis_coef()

    X_c, Y_c = Constants.KERBIN_POSITION
    mu = Constants.mu

    Pr = 0
    Ap = 0
    state_pr = (0, 0)
    state_ap = (0, 0)
    mx_vel = 0
    mn_vel = 10**10
    X, Y = [position[0]], [position[1]]

    time = 0
    semi_major = 1 / (
        2 / sqrt((position[0] - X_c) ** 2 + (position[1] - Y_c) ** 2)
        - (velocity[0] ** 2 + velocity[1] ** 2) / mu
    )
    time_on_orbit = 2 * pi * sqrt(semi_major**3 / mu)
    delta_time = time_on_orbit / 1000
    while time <= time_on_orbit:
        r = sqrt((position[0] - X_c) ** 2 + (position[1] - Y_c) ** 2)
        a = [mu * (X_c - position[0]) / r**3, mu * (Y_c - position[1]) / r**3]
        velocity = [velocity[0] + a[0] * delta_time, velocity[1] + a[1] * delta_time]
        position = [
            position[0] + velocity[0] * delta_time,
            position[1] + velocity[1] * delta_time,
        ]

        curr_velocity = sqrt(velocity[0] ** 2 + velocity[1] ** 2)
        if curr_velocity > mx_vel:
            mx_vel = curr_velocity
            Pr = r
            state_pr = (position, velocity)
        if curr_velocity < mn_vel:
            mn_vel = curr_velocity
            Ap = r
            state_ap = (position, velocity)

        X.append(position[0])
        Y.append(position[1])
        t += delta_time

        return (X, Y), (Ap, state_ap), (Pr, state_pr)


def DrawKerbinOrbit():
    X, Y = [], []
    r = Constants.KERBIN_RADIUS

    for x in range(-r, r, 10):
        d = sqrt(r**2 - x**2)
        y = -r + d
        X.append(x)
        Y.append(y)

    for x in range(r, -r, -10):
        d = sqrt(r**2 - x**2)
        y = -r - d
        X.append(x)
        Y.append(y)

    return X, Y


def FlightModel(
    rocket=Create_Rocket.Rocket(), stage=Create_Rocket.Stage(), stage_live_time=float()
):
    X_c, Y_c = Constants.KERBIN_POSITION
    mu = Constants.mu
    g = Constants.g

    time = 0
    delta_time = stage_live_time / 1000
    X = []
    Y = []
    is_apocenter_reached = False

    while time <= stage_live_time:
        rad_vec = [rocket.position[0] - X_c, rocket.position[1] - Y_c]
        r = sqrt(rad_vec[0] ** 2 + rad_vec[1] ** 2)
        velocity_vec = rocket.velocity
        curr_velocity = sqrt(rocket.velocity[0] ** 2 + rocket.velocity[1] ** 2)

        height = r - Constants.KERBIN_RADIUS
        angle = rocket.angle(height)
        pressure = Physics.Pressure(height)
        thrust = stage.curr_thrust(pressure)
        mass = stage.curr_mass(time)
        resis = Physics.Resistance(
            Physics.Density(pressure), curr_velocity, rocket.curr_resis_coef(), mass
        )

        g_x = g * (X_c - rocket.position[0]) / r
        g_y = g * (Y_c - rocket.position[1]) / r

        a = [
            sin(angle) * (thrust - resis) / mass + g_x,
            cos(angle) * (thrust - resis) / mass + g_y,
        ]

        rocket.velocity = [
            rocket.velocity[0] + a[0] * delta_time,
            rocket.velocity[1] + a[1] * delta_time,
        ]
        position = [
            position[0] + rocket.velocity[0] * delta_time,
            position[1] + rocket.velocity[1] * delta_time,
        ]

        h_square = (rad_vec[0] * velocity_vec[1] - rad_vec[1] * velocity_vec[0]) ** 2
        epsilon = (curr_velocity**2) / 2 - mu / r
        eccentricity = sqrt(1 + 2 * epsilon * h_square / (mu**2))
        semi_major = 1 / (
            2 / sqrt(rad_vec[0] ** 2 + rad_vec[1] ** 2)
            - (velocity_vec[0] ** 2 + velocity_vec[1] ** 2) / mu
        )

        apocenter = (1 + eccentricity) * semi_major
        pericenter = (1 - eccentricity) * semi_major

        if apocenter >= Constants.target_apoapsis:
            delta_vel = sqrt(mu / apocenter) * (1 - sqrt(pericenter / semi_major))
            graph, APOCENTER, _ = KerbinOrbitFlightSimulation(rocket)
            return (X, Y), graph, delta_vel

        X.append(rocket.position[0])
        Y.append(rocket.position[1])

        time += delta_time
    else:
        return (X, Y), (), 10**10
