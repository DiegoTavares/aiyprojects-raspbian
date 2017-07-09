#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def my_callback(channel):
    print "falling edge detected on 18"

GPIO.add_event_detect(18, GPIO.FALLING, callback=my_callback, bouncetime=300)

time.sleep(10)
GPIO.cleanup()           # clean up GPIO on normal exit
