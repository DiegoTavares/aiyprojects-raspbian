#!/usr/bin/env python3
import RPi.GPIO as GPIO
from datetime import datetime


class GpioSwitch(object):
    control = 0
    time_start = 0
    COMMAND_TIMEOUT = 5

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def trigger_callback(self, channel):
        # Check timeout
        if (datetime.now() - self.time_start).total_seconds() > self.COMMAND_TIMEOUT:
            self.control = 0

        if self.control == 0:
            self.time_start = datetime.now()
        self.control += 1

        if self.control == 1:
            print('control', 1)
        elif self.control == 2:
            print('control', 2)

    def start(self):
        GPIO.add_event_detect(18, GPIO.FALLING, callback=self.trigger_callback, bouncetime=300)

    def __del__(self):
        GPIO.cleanup()
