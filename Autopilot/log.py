import json
import time
import datetime
import krpc

# Флаг для остановки логгера
continue_logging = True

# Создаем файл с уникальным именем
def create_log_file():
    current_time = datetime.datetime.now().strftime("%H-%M")  # Генерируем уникальное имя файла на основе текущего времени
    file_name = f"Autopilot{current_time}.json"
    file = open(file_name, 'a')
    return file

# Записываем данные в файл
def append_to_log(file, data):
    json.dump(data, file)
    file.write('\n')

# Остановка логгера
def stop_logging():
    global continue_logging
    continue_logging = False 

# Сбор информации о ракете (каждые 0.5 секунд)
def collect_data_and_log(conn, vessel, log_file):
    time_start = conn.space_center.ut
    while continue_logging:

        # Считываиние данных
        altitude = vessel.flight().mean_altitude
        angle = vessel.auto_pilot.target_pitch
        speed = vessel.flight(vessel.orbit.body.reference_frame).speed
        cur_time = conn.space_center.ut
        mass = vessel.mass

        data = {
            "time": cur_time - time_start,
            "speed": speed,
            "angle": angle,
            "altitude": altitude,
            "mass": mass
        }
        
        # Вносим данные
        append_to_log(log_file, data)
        time.sleep(0.1)

    # Закрываем файл, когда полёт окончен
    log_file.close()