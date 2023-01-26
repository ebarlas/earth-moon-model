DEGREES = 360


class Units:
    def __init__(self, steps_per_rev=200):
        self.steps_per_rev = steps_per_rev

    def degrees_per_step(self):
        return DEGREES / self.steps_per_rev

    def steps_per_half_rev(self):
        return int(self.steps_per_rev / 2)

    def steps_per_quarter_rev(self):
        return int(self.steps_per_rev / 4)


class Steps:
    def __init__(self, units=Units(), *, steps=0, degrees=0, wrap=True):
        self.steps = 0
        self.units = units
        self.wrap = wrap
        self.add(steps)
        self.add_degrees(degrees)

    def add(self, steps, forward=True):
        self.steps += steps if forward else -steps
        if self.wrap:
            self.steps = self.steps % self.units.steps_per_rev

    def add_degrees(self, degrees):
        self.add(int(degrees / self.units.degrees_per_step()))

    def empty(self):
        return self.steps == 0

    def __add__(self, other):
        return Steps(self.units, steps=self.steps + other.steps, wrap=self.wrap)

    def __sub__(self, other):
        return Steps(self.units, steps=self.steps - other.steps, wrap=self.wrap)

    def __str__(self):
        return str(self.get())

    def __eq__(self, other):
        return self.get() == other.get()

    def __ne__(self, other):
        return self.get() != other.get()

    def get(self):
        abs_steps = abs(self.steps)
        fwd = self.steps >= 0
        if not self.wrap or abs_steps <= self.units.steps_per_half_rev():
            return fwd, abs_steps
        return not fwd, self.units.steps_per_rev - abs_steps

    def reverse(self):
        return Steps(self.units, steps=-self.steps, wrap=self.wrap)
