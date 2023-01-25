import atexit
import logging.handlers
import sys
from datetime import datetime

from adafruit_motorkit import MotorKit

import earth
import model
import motor
import sensor

logger = logging.getLogger(__name__)

STEPS_PER_REV = 200

EO_SLEEP = 0.1
ER_SLEEP = 0.05
MO_SLEEP = 0.05


def turn_off_motors(steppers):
    for stepper in steppers:
        stepper.release()


def main():
    kit = MotorKit()
    kit2 = MotorKit(address=0x61)

    eo_motor = motor.Motor(kit.stepper1, sensor.Sensor(17), EO_SLEEP, STEPS_PER_REV)
    er_motor = motor.Motor(kit.stepper2, sensor.Sensor(27), ER_SLEEP)
    mo_motor = motor.Motor(kit2.stepper1, sensor.Sensor(23), MO_SLEEP)

    atexit.register(turn_off_motors, [kit.stepper1, kit.stepper2, kit2.stepper1])

    eo_model = model.Model(eo_motor, er_motor, mo_motor, logger, STEPS_PER_REV)
    eo_model.init()

    for line in sys.stdin:
        dt = datetime.fromisoformat(line.rstrip())
        ts = earth.timescale.from_datetime(dt)
        eo_model.next(earth.earth(ts))


if __name__ == '__main__':
    main()
