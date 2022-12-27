import time
import atexit
import hall_effect
import earth
import motor
import logging
import logging.handlers
from adafruit_motorkit import MotorKit

logger = logging.getLogger(__name__)

STEPS_PER_REV = 200
DEGREES_PER_STEP = 360.0 / STEPS_PER_REV

SLEEP = 0

EO = 0 # earth orbit
ER = 1 # earth rotation
MO = 2 # moon orbit

ACTUAL = 0
FLOOR = 1
ABS = 2


def turn_off_motors(steppers):
    for stepper in steppers:
        stepper.release()


def init_logger(file_name):
    formatter = logging.Formatter('[%(asctime)s] <%(threadName)s> %(levelname)s - %(message)s')

    handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=100000, backupCount=3)
    handler.setFormatter(formatter)

    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    log.addHandler(handler)


def steps_and_floor(degrees):
    steps = degrees / DEGREES_PER_STEP
    floor = int(steps)
    return steps, floor, abs(floor)


def print_earth_model(degrees, steps):
    logger.info(f'earth_orbit[degrees={degrees[EO]:.4f}, steps={steps[EO][ACTUAL]:.4f}], '
                f'earth_rotation[degrees={degrees[ER]:.4f}, steps={steps[ER][ACTUAL]:.4f}], '
                f'moon_orbit[degrees={degrees[MO]:.4f}, steps={steps[MO][ACTUAL]:.4f}]')


def format_steps(steps):
    return "/".join(str(s) for s in steps)


def wrap(steps):
    # for example, jump from 199 to 0 should result in value 1 (0 - 199) + 200
    return steps if steps >= 0 else steps + STEPS_PER_REV


def move_to_reference_positions(earth_orbit, earth_rotation, moon_orbit):
    # scan clockwise to base position on lower earth orbit motor
    # when the magnet is directly over the hall effect sensor, it's winter solstice in the northern hemisphere
    # that is, the northern hemisphere is pointing away from the sun
    success, steps = earth_orbit.scan(False, 100, 50)
    logger.info(f'scanned clockwise, motor=earth_orbit, success={success}, steps={format_steps(steps)}')

    if not success:
        # reset position by reversing the steps taken above
        total_steps = sum(steps)
        earth_orbit.take_steps(total_steps >= 0, abs(total_steps))
        logger.info(f'reset position, motor=earth_orbit, steps={abs(total_steps)}')

        # repeat procedure above in counter-clockwise direction
        success, steps = earth_orbit.scan(True, 100, 50)
        logger.info(f'scanned counter-clockwise, motor=earth_orbit, success={success}, steps={format_steps(steps)}')

    # scan to base position on earth rotation motor
    # the prime meridian is aligned with the magnet
    # when the magnet is directly over the hall effect sensor, the prime meridian (0 degrees longitude) is also
    # directly over the sensor
    success, steps = earth_rotation.scan(True, 200, 50)
    logger.info(f'scanned counter-clockwise, motor=earth_rotation, success={success}, steps={format_steps(steps)}')

    # scan to base position on moon orbit motor
    # new moon (on sun side of earth) aligned with the magnet
    # when the magnet is directly over the hall effect sensor, the lunar phase is new moon
    success, steps = moon_orbit.scan(True, 200, 50)
    logger.info(f'scanned counter-clockwise, motor=moon_orbit, success={success}, steps={format_steps(steps)}')


def main():
    init_logger('earth_model.log')

    kit = MotorKit()
    kit2 = MotorKit(address=0x61)

    earth_orbit = motor.Motor(kit.stepper1, hall_effect.Sensor(17))
    earth_rotation = motor.Motor(kit.stepper2, hall_effect.Sensor(27))
    moon_orbit = motor.Motor(kit2.stepper1, hall_effect.Sensor(23))

    atexit.register(turn_off_motors, [earth_orbit, earth_rotation, moon_orbit])

    move_to_reference_positions(earth_orbit, earth_rotation, moon_orbit)

    em = earth.earth_model_now()
    degrees = [em.earth_orbit_degrees, em.earth_rotation_degrees, em.moon_orbit_degrees]
    steps = [steps_and_floor(d) for d in degrees]
    print_earth_model(degrees, steps)

    # -180 to 180, with positive referring to "forward" direction (counter-clockwise when observed from above)
    earth_orbit.take_steps(steps[EO][FLOOR] > 0, steps[EO][ABS])

    # reverse earth-orbit operation to re-reposition prime meridian at solar noon
    earth_rotation.take_steps(steps[EO][FLOOR] < 0, steps[EO][ABS])
    earth_rotation.take_steps(True, steps[ER][FLOOR])

    # reverse earth-orbit operation to re-reposition at new moon lunar phase
    moon_orbit.take_steps(steps[EO][FLOOR] < 0, steps[EO][ABS])
    moon_orbit.take_steps(True, steps[MO][FLOOR])

    while True:
        em = earth.earth_model_now()
        next_degrees = [em.earth_orbit_degrees, em.earth_rotation_degrees, em.moon_orbit_degrees]
        next_steps = [steps_and_floor(d) for d in next_degrees]
        print_earth_model(next_degrees, next_steps)

        if next_steps[EO][FLOOR] != steps[EO][FLOOR]:
            delta = next_steps[EO][FLOOR] - steps[EO][FLOOR]
            abs_delta = abs(delta)
            earth_orbit.take_steps(delta > 0, abs_delta)
            earth_rotation.take_steps(delta < 0, abs_delta)
            moon_orbit.take_steps(delta < 0, abs_delta)

        if next_steps[ER][FLOOR] != steps[ER][FLOOR]:
            delta = wrap(next_steps[ER][FLOOR] - steps[ER][FLOOR])
            earth_rotation.take_steps(True, delta)

        if next_steps[MO][FLOOR] != steps[MO][FLOOR]:
            delta = wrap(next_steps[MO][FLOOR] - steps[MO][FLOOR])
            moon_orbit.take_steps(True, delta)

        steps = next_steps
        time.sleep(60)


if __name__ == '__main__':
    main()
