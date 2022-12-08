import time

FORWARD = 1
BACKWARD = 2


def take_steps(forward, motor, steps, sleep):
    """
    Take a number of steps forward or backward, with an optional pause in between each step.
    """
    for i in range(steps):
        motor.onestep(direction=FORWARD if forward else BACKWARD)
        time.sleep(sleep)


def step_until_sensor_signal(forward, motor, sensor, max_steps, sleep, target_signal):
    """
    Take steps until sensor yields a target signal or the maximum number of steps is reached.
    Returns a tuple of (1) bool denoting if sensor yielded target signal and (2) number of steps taken.
    """
    steps = 0
    found = False
    while not found and steps < max_steps:
        if sensor.sensing() == target_signal:
            found = True
        else:
            motor.onestep(direction=FORWARD if forward else BACKWARD)
            time.sleep(sleep)
            steps += 1
    return found, steps


def step_while_over_sensor(forward, motor, sensor, max_steps, sleep):
    return step_until_sensor_signal(forward, motor, sensor, max_steps, sleep, False)


def step_until_over_sensor(forward, motor, sensor, max_steps, sleep):
    return step_until_sensor_signal(forward, motor, sensor, max_steps, sleep, True)


def scan(forward, motor, sensor, max_scan_steps, max_sensor_steps, sleep):
    """
    Scan that steps the motor directly over the middle of the sensing region of the sensor.
    Procedure:
        1. Step until off of sensor in negative direction
        2. Step until on sensor in positive direction
        3. Step until off of sensor in positive direction
        4. Step half way bay in negative direction
    Return tuple with (1) bool indicating success status and (2) list of steps taken
    """
    all_steps = []
    found, steps = step_while_over_sensor(not forward, motor, sensor, max_sensor_steps, sleep)
    all_steps.append(-steps)
    if not found:
        return False, all_steps

    found, steps = step_until_over_sensor(forward, motor, sensor, max_scan_steps, sleep)
    all_steps.append(steps)
    if not found:
        return False, all_steps

    found, steps = step_while_over_sensor(forward, motor, sensor, max_sensor_steps, sleep)
    all_steps.append(steps)
    if not found:
        return False, all_steps

    half = int(steps / 2)
    take_steps(not forward, motor, half, sleep)
    all_steps.append(-half)
    return True, all_steps
