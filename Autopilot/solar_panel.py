import krpc


conn = krpc.connect()  # подключаемся к серверу 
vessel = conn.space_center.active_vessel  # активный корабль
control = vessel.control  # контролировать корабль

antennas = vessel.parts.antennas
solar_pannels = vessel.parts.solar_panels

# Раскрываем антенны 
for a in antennas:
    if a.deployable:
        a.deployed = True

# Раскрываем панели
for s in solar_pannels:
    if s.deployable:
        s.deployed = True