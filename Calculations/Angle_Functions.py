from math import pi, sqrt


def Linear(pos0, pos1):
    k = (pos1[1] - pos0[1]) / (pos1[0] - pos0[0])
    b = pos0[1] - pos0[0] * k

    def func(x):
        return min(max(k * x + b, 0), pi / 2)

    return func


def Parabolic(pos0, pos1):
    p, q = pos0
    s, r = pos1
    a = (q - r) / (2 * p * s - s**2 - p**2)
    b = -2 * a * p
    c = q - a * p**2 - b * p

    def func(x):
        if x < pos0[0] or x > pos1[0]:
            return pos0[1] if x < pos0[0] else pos1[1]
        return a * x**2 + b * x + c

    return func


def Elliptic(pos0, pos1):
    p, q = pos0
    s, r = pos1
    a = s - p
    b = r - q

    def func(x):
        if x < pos0[0] or x > pos1[0]:
            return pos0[1] if x < pos0[0] else pos1[1]
        return sqrt(b**2 - (b / a) ** 2 * (x - s) ** 2) + q

    return func
