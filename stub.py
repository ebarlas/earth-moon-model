class MotorAssembly:
    def __init__(self, start_degrees, sensor_ranges):
        self.degrees = start_degrees
        self.sensor_ranges = sensor_ranges

    def onestep(self, direction):
        self.degrees += 1 if direction == 1 else -1  # 1 degree per step
        if self.degrees < 0:
            self.degrees += 360
        if self.degrees > 360:
            self.degrees -= 360

    def sensing(self):
        return any(r[0] <= self.degrees <= r[1] for r in self.sensor_ranges)
