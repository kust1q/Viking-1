class Rocket:

    def __init__(self, angle_func):
        self.curr_mass = 0  # текущая масса
        self.position = (0, 0)
        self.velocity = (0, 0)
        self.stages = []  # массив с ступенями(движками)
        self.angle_func = angle_func

    def add_stage(self, stage):
        self.stages += [stage]

    def unhook_stage(self):
        if len(self.stages) > 1:
            self.stages = self.stages.pop()
            print("Stage unhooked successfully")
        else:
            print("Nothing to unhook")

    def last_curr_mass(self):
        if len(self.stages) > 0:
            self.curr_mass = self.stages[0].get_last_mass()
            return self.curr_mass

    def curr_resis_coef(self):
        sup_num1, sup_num2 = 0, 0
        for stage in self.stages:
            for elem in stage.resis_coef:
                sup_num1 += elem[0] * elem[1]
                sup_num2 += elem[0]
        return sup_num1 / sup_num2

    def choose_angle_function(self, function):
        self.angle_func = function

    def angle(self, h):
        return self.angle_func(h)


class Stage:

    def __init__(
        self,
        vac_thrust,
        ground_thrust,
        start_mass,
        end_mass,
        resis_coef,
        fuel_consump,
        full_fuel,
    ):
        self.vac_thrust = vac_thrust  # тяга в вакууме
        self.ground_thrust = ground_thrust  # тяга у земли
        self.start_mass = start_mass  # начальная масса
        self.end_mass = end_mass  # конечная масса
        self.resis_coef = (
            resis_coef  # массив [(масса детали в тоннах, кэф сопротивления), ...]
        )
        self.fuel_consump = fuel_consump  # расход топлива
        self.full_fuel = full_fuel  # максимальное количество топлива
        self.curr_mass = self.start_mass  # текущая масса
        self.delta_thrust = self.ground_thrust - self.vac_thrust  # разность тяг
        self.max_time_moving = full_fuel / fuel_consump
        self.max_distance = (self.end_mass - self.start_mass) / self.max_time_moving

    def curr_thrust(self, pressure):
        return max(
            min(self.vac_thrust + self.delta_thrust * pressure, self.vac_thrust),
            self.ground_thrust,
        )

    def curr_mass(self, time):
        self.curr_mass = max(
            min(self.start_mass + self.max_distance * time, self.start_mass),
            self.end_mass,
        )
        return self.curr_mass

    def get_last_mass(self):
        return self.curr_mass
