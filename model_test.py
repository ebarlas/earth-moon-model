import unittest
from collections import namedtuple

import model
import motor
import stub

Earth = namedtuple('Earth', ['eo_degrees', 'er_degrees', 'mo_degrees'])


class TestLogger:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


class TestModel(unittest.TestCase):
    def test_model(self):
        sensor_range = [(350, 360), (0, 10)]
        eo_tm = stub.MotorAssembly(100, sensor_range)
        er_tm = stub.MotorAssembly(200, sensor_range)
        mo_tm = stub.MotorAssembly(300, sensor_range)
        eo_motor = motor.Motor(eo_tm, eo_tm)
        er_motor = motor.Motor(er_tm, er_tm)
        mo_motor = motor.Motor(mo_tm, mo_tm)
        logger = TestLogger()
        em = model.Model(eo_motor, er_motor, mo_motor, logger, 360)
        em.init()
        self.assertEqual(-100, eo_motor.steps)
        self.assertEqual(160, er_motor.steps)
        self.assertEqual(60, mo_motor.steps)
        em.next(Earth(90, 30, 60))
        self.assertEqual(-100 - 90, eo_motor.steps)
        self.assertEqual(160 + 90 + 30, er_motor.steps)
        self.assertEqual(60 + 90 + 60, mo_motor.steps)
        em.next(Earth(95, 40, 80))  # +5, +10, +20
        self.assertEqual(-100 - 90 - 5, eo_motor.steps)
        self.assertEqual(160 + 90 + 30 + 5 + 10, er_motor.steps)
        self.assertEqual(60 + 90 + 60 + 5 + 20, mo_motor.steps)
        em.next(Earth(190, 40, 80))  # 190 maps to 170, +265 steps
        self.assertEqual(-100 - 90 - 5 + 265, eo_motor.steps)
        self.assertEqual(160 + 90 + 30 + 5 + 10 + 95, er_motor.steps)  # fewest reverse steps +95
        self.assertEqual(60 + 90 + 60 + 5 + 20 + 95, mo_motor.steps)

    def test_multi_scan(self):
        sensor_range = [(350, 360), (0, 10)]
        eo_tm = stub.MotorAssembly(200, sensor_range)
        er_tm = stub.MotorAssembly(0, sensor_range)
        mo_tm = stub.MotorAssembly(355, sensor_range)
        eo_motor = motor.Motor(eo_tm, eo_tm)
        er_motor = motor.Motor(er_tm, er_tm)
        mo_motor = motor.Motor(mo_tm, mo_tm)
        logger = TestLogger()
        em = model.Model(eo_motor, er_motor, mo_motor, logger, 360)
        em.init()
        self.assertEqual(160, eo_motor.steps)
        self.assertEqual(0, er_motor.steps)
        self.assertEqual(5, mo_motor.steps)
        em.next(Earth(25, 0, 330))
        self.assertEqual(160 - 25, eo_motor.steps)
        self.assertEqual(25, er_motor.steps)
        self.assertEqual(5 + 25 - 30, mo_motor.steps)  # shortest path for +330 is -30
        em.next(Earth(25, 0, 5))
        self.assertEqual(5 + 25 - 30 + 35, mo_motor.steps)
