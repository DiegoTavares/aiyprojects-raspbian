#!/usr/bin/env python3
import RPi.GPIO as GPIO
from datetime import datetime
from threading import Timer


class GpioSwitch(object):
    control = 0
    COMMAND_TIMEOUT = 5

    def __init__(self, actions):
        self.time_start = datetime.now()
        self.actions = actions
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def trigger_callback(self, channel):
        # Check timeout
        if (datetime.now() - self.time_start).total_seconds() > self.COMMAND_TIMEOUT:
            self.control = 0

        if self.control == 0:
            self.time_start = datetime.now()
            Timer(5.0, self.execute).start()

        self.control += 1

    def execute(self):
        if self.control > len(self.actions):
            print('Invalid action')
        else:
            action = self.actions[self.control - 1]
            print('Executing action', action.__name__)
            action()

    def start(self):
        GPIO.add_event_detect(18, GPIO.FALLING, callback=self.trigger_callback, bouncetime=300)

    def __del__(self):
        GPIO.cleanup()
