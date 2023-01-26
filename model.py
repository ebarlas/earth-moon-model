import steps


class Model:
    def __init__(self, eo_motor, er_motor, mo_motor, logger, steps_per_rev):
        self.eo_motor = eo_motor
        self.er_motor = er_motor
        self.mo_motor = mo_motor
        self.logger = logger
        self.units = steps.Units(steps_per_rev)
        self.steps = [steps.Steps(self.units, wrap=False), steps.Steps(self.units), steps.Steps(self.units)]

    def init(self):
        def fmt(steps):
            return '/'.join(str(s) for s in steps)

        spr = self.units.steps_per_rev
        sphr = self.units.steps_per_half_rev()
        spqr = self.units.steps_per_quarter_rev()

        # scan clockwise (looking from above) to base position on lower earth orbit motor
        # when the magnet is directly over the hall effect sensor, it's winter solstice in the northern hemisphere
        # that is, the northern hemisphere is pointing away from the sun
        success, steps = self.eo_motor.scan(False, sphr, spqr)
        self.logger.info(f'scanned back, motor=earth_orbit, success={success}, steps={fmt(steps)}')

        if not success:
            # reset position by reversing the steps taken above
            total_steps = sum(steps)
            self.eo_motor.take_steps(total_steps >= 0, abs(total_steps))
            self.logger.info(f'reset position, motor=earth_orbit, steps={abs(total_steps)}')

            # repeat procedure above in counter-clockwise direction
            success, steps = self.eo_motor.scan(True, sphr, spqr)
            self.logger.info(f'scanned forward, motor=earth_orbit, success={success}, steps={fmt(steps)}')
            if not success:
                raise ValueError('unable to locate earth-orbit reference position')

        # scan to base position on earth rotation motor
        # the prime meridian is aligned with the magnet
        # when the magnet is directly over the hall effect sensor, the prime meridian (0 degrees longitude) is also
        # directly over the sensor
        success, steps = self.er_motor.scan(True, spr, spqr)
        self.logger.info(f'scanned forward, motor=earth_rotation, success={success}, steps={fmt(steps)}')
        if not success:
            raise ValueError('unable to locate earth-rotation reference position')

        # scan to base position on moon orbit motor
        # new moon (on sun side of earth) aligned with the magnet
        # when the magnet is directly over the hall effect sensor, the lunar phase is new moon
        success, steps = self.mo_motor.scan(True, spr, spqr)
        self.logger.info(f'scanned forward, motor=moon_orbit, success={success}, steps={fmt(steps)}')
        if not success:
            raise ValueError('unable to locate moon-orbit reference position')

    def _rescale_earth_orbit(self, degrees):
        """
        Rescale earth orbit degrees 0 to 360 maps to 0 to -180 and 180 back to 0.
        """
        if degrees <= 180:
            return -degrees  # [0, 180] -> [0, -180]
        d = degrees - 180  # [180, 360] -> [0, 180]
        return 180 - d  # [0, 180] -> [180, 0]

    def _log_position(self, earth, eo_steps, er_steps, mo_steps):
        self.logger.info(f'earth_orbit[degrees={earth.eo_degrees:.4f}, steps={eo_steps.steps}], '
                         f'earth_rotation[degrees={earth.er_degrees:.4f}, steps={er_steps.steps}], '
                         f'moon_orbit[degrees={earth.mo_degrees:.4f}, steps={mo_steps.steps}]')

    def next(self, earth):
        eo_steps = steps.Steps(self.units, degrees=self._rescale_earth_orbit(earth.eo_degrees), wrap=False)
        er_steps = steps.Steps(self.units, degrees=earth.er_degrees)
        mo_steps = steps.Steps(self.units, degrees=earth.mo_degrees).reverse()  # reverse since moon is inverted
        self._log_position(earth, eo_steps, er_steps, mo_steps)

        eo_steps_last, er_steps_last, mo_steps_last = self.steps

        eo_steps_diff = eo_steps - eo_steps_last
        er_steps_diff = (er_steps - er_steps_last) + eo_steps_diff.reverse()
        mo_steps_diff = (mo_steps - mo_steps_last) + eo_steps_diff

        self.eo_motor.take_steps(*eo_steps_diff.get())
        self.er_motor.take_steps(*er_steps_diff.get())
        self.mo_motor.take_steps(*mo_steps_diff.get())
        self.steps = [eo_steps, er_steps, mo_steps]
