DEGREES = 360


class Model:
    def __init__(self, eo_motor, er_motor, mo_motor, logger, steps_per_rev):
        self.eo_motor = eo_motor
        self.er_motor = er_motor
        self.mo_motor = mo_motor
        self.logger = logger
        self.steps_per_rev = steps_per_rev
        self.steps = None

    def _steps_per_half_rev(self):
        return int(self.steps_per_rev / 2)

    def _steps_per_quarter_rev(self):
        return int(self.steps_per_rev / 4)

    def _degrees_per_step(self):
        return DEGREES / self.steps_per_rev

    def _fmt_steps(self, steps):
        return "/".join(str(s) for s in steps)

    def init(self):
        # scan clockwise (looking from above) to base position on lower earth orbit motor
        # when the magnet is directly over the hall effect sensor, it's winter solstice in the northern hemisphere
        # that is, the northern hemisphere is pointing away from the sun
        success, steps = self.eo_motor.scan(False, self._steps_per_half_rev(), self._steps_per_quarter_rev())
        self.logger.info(f'scanned back, motor=earth_orbit, success={success}, steps={self._fmt_steps(steps)}')

        if not success:
            # reset position by reversing the steps taken above
            total_steps = sum(steps)
            self.eo_motor.take_steps(total_steps >= 0, abs(total_steps))
            self.logger.info(f'reset position, motor=earth_orbit, steps={abs(total_steps)}')

            # repeat procedure above in counter-clockwise direction
            success, steps = self.eo_motor.scan(True, self._steps_per_half_rev(), self._steps_per_quarter_rev())
            self.logger.info(f'scanned forward, motor=earth_orbit, success={success}, steps={self._fmt_steps(steps)}')
            if not success:
                raise ValueError('unable to locate earth-orbit reference position')

        # scan to base position on earth rotation motor
        # the prime meridian is aligned with the magnet
        # when the magnet is directly over the hall effect sensor, the prime meridian (0 degrees longitude) is also
        # directly over the sensor
        success, steps = self.er_motor.scan(True, self.steps_per_rev, self._steps_per_quarter_rev())
        self.logger.info(f'scanned forward, motor=earth_rotation, success={success}, steps={self._fmt_steps(steps)}')
        if not success:
            raise ValueError('unable to locate earth-rotation reference position')

        # scan to base position on moon orbit motor
        # new moon (on sun side of earth) aligned with the magnet
        # when the magnet is directly over the hall effect sensor, the lunar phase is new moon
        success, steps = self.mo_motor.scan(True, self.steps_per_rev, self._steps_per_quarter_rev())
        self.logger.info(f'scanned forward, motor=moon_orbit, success={success}, steps={self._fmt_steps(steps)}')
        if not success:
            raise ValueError('unable to locate moon-orbit reference position')

    def _rescale(self, degrees):
        """
        Rescale earth orbit degrees 0 to 360 maps to 0 to -180 and 180 back to 0.
        """
        if degrees <= 180:
            return -degrees  # [0, 180] -> [0, -180]
        d = degrees - 180  # [180, 360] -> [0, 180]
        return 180 - d  # [0, 180] -> [180, 0]

    def _steps_and_floor(self, degrees):
        """
        Given degrees, calculate corresponding (1) steps, (2) floor(steps), (3) abs(floor(step))
        """
        steps = degrees / self._degrees_per_step()
        floor = int(steps)
        return steps, floor, abs(floor)

    def _print(self, degrees, steps):
        eo_degrees, er_degrees, mo_degrees = degrees
        eo_steps, er_steps, mo_steps = steps
        self.logger.info(f'earth_orbit[degrees={eo_degrees:.4f}, steps={eo_steps:.4f}], '
                         f'earth_rotation[degrees={er_degrees:.4f}, steps={er_steps:.4f}], '
                         f'moon_orbit[degrees={mo_degrees:.4f}, steps={mo_steps:.4f}]')

    def _reverse_steps(self, forward, steps):
        """
        Reverse steps in the direction with the fewest steps.
        """
        return self._fewest_steps(not forward, steps)

    def _fewest_steps(self, forward, steps):
        if steps <= self._steps_per_half_rev():
            return forward, steps
        return not forward, self.steps_per_rev - steps

    def _wrap(self, steps):
        # for example, jump from 199 to 0 should result in value 1 (0 - 199) + 200
        if steps >= 0:
            return steps
        return steps + self.steps_per_rev

    def _first_steps(self, earth):
        eo_degrees, er_degrees, mo_degrees = [self._rescale(earth.eo_degrees), earth.er_degrees, earth.mo_degrees]
        eo_steps, eo_floor, eo_abs = self._steps_and_floor(eo_degrees)
        er_steps, er_floor, _ = self._steps_and_floor(er_degrees)
        mo_steps, mo_floor, _ = self._steps_and_floor(mo_degrees)
        self._print([eo_degrees, er_degrees, mo_degrees], [eo_steps, er_steps, mo_steps])

        dir_steps = (eo_floor > 0, eo_abs)
        rev_steps = self._reverse_steps(*dir_steps)

        self.eo_motor.take_steps(*dir_steps)
        self.er_motor.take_steps(*rev_steps)
        self.mo_motor.take_steps(*dir_steps) # since motor is inverted, this is effectively in reverse
        self.logger.info(f'op=eo_init, fwd={dir_steps[0]}, delta={dir_steps[1]}')

        er_fewest = self._fewest_steps(True, er_floor)
        self.er_motor.take_steps(*er_fewest)
        self.logger.info(f'op=er_init, fwd={er_fewest[0]}, steps={er_fewest[1]}')

        mo_fewest = self._fewest_steps(True, mo_floor)
        self.mo_motor.take_steps(*self._reverse_steps(*mo_fewest))
        self.logger.info(f'op=mo_init, fwd={mo_fewest[0]}, steps={mo_fewest[1]}')

        self.steps = [eo_floor, er_floor, mo_floor]

    def _next_steps(self, earth):
        eo_degrees, er_degrees, mo_degrees = [self._rescale(earth.eo_degrees), earth.er_degrees, earth.mo_degrees]
        eo_steps, eo_floor, _ = self._steps_and_floor(eo_degrees)
        er_steps, er_floor, _ = self._steps_and_floor(er_degrees)
        mo_steps, mo_floor, _ = self._steps_and_floor(mo_degrees)
        self._print([eo_degrees, er_degrees, mo_degrees], [eo_steps, er_steps, mo_steps])

        eo_floor_last, er_floor_last, mo_floor_last = self.steps

        if eo_floor != eo_floor_last:
            delta = eo_floor - eo_floor_last
            abs_delta = abs(delta)
            dir_steps = (delta > 0, abs_delta)
            rev_steps = self._reverse_steps(*dir_steps)
            self.eo_motor.take_steps(*dir_steps)
            self.er_motor.take_steps(*rev_steps)
            self.mo_motor.take_steps(*dir_steps)
            self.logger.info(f'op=eo_diff, fwd={dir_steps[0]}, delta={dir_steps[1]}')

        if er_floor != er_floor_last:
            delta = self._fewest_steps(True, self._wrap(er_floor - er_floor_last))
            self.er_motor.take_steps(*delta)
            self.logger.info(f'op=er_diff, fwd={delta[0]}, delta={delta[1]}')

        if mo_floor != mo_floor_last:
            delta = self._fewest_steps(True, self._wrap(mo_floor - mo_floor_last))
            self.mo_motor.take_steps(*self._reverse_steps(*delta))
            self.logger.info(f'op=mo_diff, fwd={delta[0]}, delta={delta[1]}')

        self.steps = [eo_floor, er_floor, mo_floor]

    def next(self, time):
        if not self.steps:
            self._first_steps(time)
        else:
            self._next_steps(time)
