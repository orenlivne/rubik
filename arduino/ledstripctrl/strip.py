#!/usr/bin/env python
"""
strip.py - Control a strip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.pde Arduino program before running this script.

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
"""

import serial, time
from time import sleep

SERIAL_DEVICE = 'COM3'  # '/dev/cu.usbserial-A900adMy' # Or 'COM3' on my windows machine

# Number of LED lights on the strip
led_count = 32

def clearreadbuffer(ser):
    print ser.readline().strip()

def bluefadein(ser):
    for ii in xrange(128, 256):
        print "--"
        for i in xrange(led_count):
            outval = "%02X%02X%02X%02X" % (i, 0, 0, ii)
            # print outval
            ser.write("%s\n" % outval)
            clearreadbuffer(ser)
    
        ser.write('FF\n')
        clearreadbuffer(ser)
        # time.sleep(1)

def show(ser):
    ser.write('FF\n')
    print ser.readline()

def ledset(ser, led, r, g, b):
    outval = "%02X%02X%02X%02X" % (led, r, g, b)
    print outval
    ser.write("%s\n" % outval)
    print ser.readline()

def glitchtest(ser):
    for ii in [0, 0x20, 0x21]:
        for i in xrange(led_count - 1):
            ledset(ser, i, 0, 0, ii)
        show(ser)
        sleep(1)
        print "---"

def blinktest(ser):
    while True:
        for i in xrange(led_count):
            ledset(ser, i, 0, 0, 0)
        show(ser)
        sleep(0.5)
        for i in xrange(led_count):
            ledset(ser, i, 255, 255, 255)
        show(ser)
        sleep(0.5)

def cylon(ser):
    i = last = 0
    direction = 1
    # for i in xrange(0, 32):
    #  ledset(ser, i, 0, 0, 0)
    #  show(ser)

    while True:
        ledset(ser, last, 0, 0, 0)
        ledset(ser, i, 0, 255, 0)
        show(ser)
        last = i
        i = i + direction
        if i <= 0:
            direction = 1
        if i >= led_count - 1:
            direction = -1
        # sleep(0.05) 

if __name__ == '__main__':
    print "Connecting"
    ser = serial.Serial(SERIAL_DEVICE, 115200)
    time.sleep(2)
    print "Running"
    #cylon(ser)
    blinktest(ser)
