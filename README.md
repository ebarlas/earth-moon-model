## Overview

Earth Moon Model (EMM) is a tabletop digital art project that combines a Raspberry Pi
computer with sensors and actuators to create a realistic model of the Earth and
the Moon in their orbits.

## Design

The image on the left is a rendering of EMM. The design source is
freely available on [TinkerCAD](https://www.tinkercad.com/things/2K7GgXmbFCp).

The image on the right illustrates the perspective of the EMM observer.
The observer follows the Earth as it travels around the Sun, with the Sun always
due west of the observer.

| Model | Model Perspective                 |
|----------------|-----------------------------------|
| ![](img/earth-moon-model-annotated.png) | ![](img/earth-model-camera-2.png) |

## Parts

* Raspberry Pi Zero W
* Adafruit Stepper Motor, NEMA-17 size, 200 steps/rev, 12V 350mA (x3)
* Adafruit Stepper Motor HAT (x2)
* Hall effect sensor (x3)
* Tiny round disk magnet (x3)
* 5V 2A power supply

## Software

EMM is running on a Raspberry Pi Zero W with [DietPi OS](https://dietpi.com/docs/).
DietPi is a highly optimized and minimal Debian-based Linux distribution.

At the time of this writing, DietPi version `8.9.2` is installed. It runs atop Linux kernel version `5.15`.

```
# uname -a
Linux DietPi 5.15.61+ #1579 Fri Aug 26 11:08:59 BST 2022 armv6l GNU/Linux
```

Python3 is required.

```
apt-get install python3
apt-get install python3-pip
```

The following Python package dependencies are required:

* [`skyfield`](https://rhodesmill.org/skyfield/) - library for calculating astronomical predictions
* [`adafruit_motorkit`](https://github.com/adafruit/Adafruit_CircuitPython_MotorKit) - library for controlling stepper motors
* [`RPi.GPIO`](https://pypi.org/project/RPi.GPIO) - library for interacting with Raspberry Pi GPIO pins

```
pip3 install skyfield
pip3 install adafruit-circuitpython-motorkit
pip3 install RPi.GPIO
```

The following was also necessary with my setup. See https://github.com/numpy/numpy/issues/14553.

```
apt-get install libatlas-base-dev
```

## Assembly

## Current Draw

The Raspberry Pi Zero W alone draws about 113 mA of current.

Each motor draws roughly an additional 140 mA of current.

Together, the system draws about 538 mA of current as measured with a multimeter.

Tests were conducted by activating the stepper motors one at a time via a simple
Python REPL.

```python
from adafruit_motorkit import MotorKit
kit = MotorKit()
kit.stepper1.onestep() # engage 1st motor
kit.stepper2.onestep() # engage 2nd motor
kit2 = MotorKit(address=0x61)
kit2.stepper1.onestep() # engage 3rd motor
```

| RPi                         | 1 Motor                     | 2 Motors                    | 3 Motors                    |
|-----------------------------|-----------------------------|-----------------------------|-----------------------------|
| ![](img/current_draw_1.jpg) | ![](img/current_draw_2.jpg) | ![](img/current_draw_3.jpg) | ![](img/current_draw_4.jpg) |