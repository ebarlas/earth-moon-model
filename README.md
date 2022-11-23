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

| Model | Model Perspective               |
|----------------|---------------------------------|
| ![](img/earth-moon-model-annotated.png) | ![](img/earth-model-camera.png) |

## Parts

* Raspberry Pi Zero W
* Adafruit Stepper Motor, NEMA-17 size, 200 steps/rev, 12V 350mA (x3)
* Adafruit Stepper Motor HAT (x2)
* Hall effect sensor (x3)
* Tiny round disk magnet (x3)
* 5V 2A power supply

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