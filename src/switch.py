#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time


class GpioSwitch(object):
    control = 0

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        pass

    def my_callback(self, channel):
        print("falling edge detected on 18")

    def start(self):
        GPIO.add_event_detect(18, GPIO.FALLING, callback=self.my_callback, bouncetime=300)

    def __del__(self):
        GPIO.cleanup()
