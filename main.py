import atexit
import logging
import logging.handlers
import time

from adafruit_motorkit import MotorKit

import earth
import model
import motor
import sensor

logger = logging.getLogger(__name__)

STEPS_PER_REV = 200

SLEEP = 0


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


def main():
    init_logger('earth_model.log')

    kit = MotorKit()
    kit2 = MotorKit(address=0x61)

    eo_motor = motor.Motor(kit.stepper1, sensor.Sensor(17), SLEEP, STEPS_PER_REV)
    er_motor = motor.Motor(kit.stepper2, sensor.Sensor(27), SLEEP)
    mo_motor = motor.Motor(kit2.stepper1, sensor.Sensor(23), SLEEP)

    atexit.register(turn_off_motors, [kit.stepper1, kit.stepper2, kit2.stepper1])

    eo_model = model.Model(eo_motor, er_motor, mo_motor, logger, STEPS_PER_REV)
    eo_model.init()
    while True:
        eo_model.next(earth.timescale.now())
        time.sleep(60)


if __name__ == '__main__':
    main()
