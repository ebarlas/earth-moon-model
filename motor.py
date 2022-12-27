import time

FORWARD = 1
BACKWARD = 2


class Motor:
    def __init__(self, stepper, sensor, sleep=0):
        self.stepper = stepper
        self.sensor = sensor
        self.sleep = sleep
        self.steps = 0
        self.abs_steps = 0

    def _sleep(self):
        time.sleep(self.sleep)

    def _onestep(self, forward):
        self.stepper.onestep(direction=FORWARD if forward else BACKWARD)
        self.steps += 1 if forward else -1
        self.abs_steps += 1
        self._sleep()

    def take_steps(self, forward, steps):
        """
        Take a number of steps forward or backward
        """
        for i in range(steps):
            self._onestep(forward)

    def _step_until_sensor_signal(self, forward, max_steps, target_signal):
        """
        Take steps until sensor yields a target signal or the maximum number of steps is reached.
        Returns a tuple of (1) bool denoting if sensor yielded target signal and (2) number of steps taken.
        """
        steps = 0
        found = False
        while not found and steps < max_steps:
            if self.sensor.sensing() == target_signal:
                found = True
            else:
                self._onestep(forward)
                steps += 1
        return found, steps

    def _step_while_over_sensor(self, forward, max_steps):
        return self._step_until_sensor_signal(forward, max_steps, False)

    def _step_until_over_sensor(self, forward, max_steps):
        return self._step_until_sensor_signal(forward, max_steps, True)

    def scan(self, forward, max_scan_steps, max_sensor_steps):
        """
        Scan that steps the motor directly over the middle of the sensing region of the sensor.
        Procedure:
            1. Step until off of sensor in negative direction
            2. Step until on sensor in positive direction
            3. Step until off of sensor in positive direction
            4. Step half way back in negative direction
        Return tuple with (1) bool indicating success status and (2) list of steps taken in target direction
        """
        all_steps = []
        found, steps = self._step_while_over_sensor(not forward, max_sensor_steps)
        all_steps.append(-steps)
        if not found:
            return False, all_steps

        found, steps = self._step_until_over_sensor(forward, max_scan_steps)
        all_steps.append(steps)
        if not found:
            return False, all_steps

        found, steps = self._step_while_over_sensor(forward, max_sensor_steps)
        all_steps.append(steps)
        if not found:
            return False, all_steps

        half = int(steps / 2)
        self.take_steps(not forward, half)
        all_steps.append(-half)
        return True, all_steps
