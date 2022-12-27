import unittest

import motor


class MotorAssembly:
    def __init__(self, start_degrees, sensor_range):
        self.degrees = start_degrees
        self.sensor_range = sensor_range

    def onestep(self, direction):
        self.degrees += 1 if direction == 1 else -1  # 1 degree per step

    def sensing(self):
        return self.sensor_range[0] <= self.degrees <= self.sensor_range[1]


class TestMotor(unittest.TestCase):
    def test_scan(self):
        ma = MotorAssembly(0, (60, 79))
        m = motor.Motor(ma, ma)
        status, steps = m.scan(True, 100, 50)
        self.assertTrue(status)
        self.assertEqual(4, len(steps))
        self.assertEqual(0, steps[0])  # no initial steps needed to scan off of sensor
        self.assertEqual(60, steps[1])  # 60 steps to scan to sensing region
        self.assertEqual(20, steps[2])  # 20 steps to scan off of sensing region
        self.assertEqual(-10, steps[3])  # -10 steps to scan to the middle of sensing region
        self.assertEqual(70, ma.degrees)  # motor should be at 70 degrees now

    def test_scan_sensor_not_found(self):
        ma = MotorAssembly(0, (60, 79))
        m = motor.Motor(ma, ma)
        status, steps = m.scan(True, 50, 50)
        self.assertFalse(status)
        self.assertEqual(2, len(steps))
        self.assertEqual(0, steps[0])  # no initial steps needed to scan off of sensor
        self.assertEqual(50, steps[1])  # sensing region not reached after max 50 steps
        self.assertEqual(50, ma.degrees)  # motor should be at 50 degrees now

    def test_scan_sensing_region_too_large(self):
        ma = MotorAssembly(100, (0, 200))
        m = motor.Motor(ma, ma)
        status, steps = m.scan(True, 50, 50)
        self.assertFalse(status)
        self.assertEqual(1, len(steps))
        self.assertEqual(-50, steps[0])  # sensing region not departed after max 50 steps
        self.assertEqual(50, ma.degrees)  # motor should be at 50 degrees now
