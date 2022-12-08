import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)


class Sensor():
    def __init__(self, pin):
        self.pin = pin
        gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)

    def sensing(self):
        return not gpio.input(self.pin)
