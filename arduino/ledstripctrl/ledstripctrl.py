#!/usr/bin/env python
"""
strip.py - Control a strip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.ino Arduino program before running this script.

Usage: ledstripctrl <arduino-usb-port> <led-count>

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
"""

import serial, time, sys
import matplotlib.pyplot as plt
from time import sleep
from MagicCube.code.cube_interactive import Cube

class ArduinoController(object):
    def __init__(self, serial_stream, led_count):
        self._serial_buffer = serial_stream
        self._led_count = led_count
        
    def _clear_read_buffer(self):
        print self._serial_stream.readline().strip()
    
    def _show(self):
        self._serial_stream.write('FF\n')
        print self._serial_stream.readline()
    
    def _led_set(self, led, r, g, b):
        outval = "%02X%02X%02X%02X" % (led, r, g, b)
        print outval
        self._serial_stream.write('%s\n' % outval)
        print self._serial_stream.readline()
    
    def blink_test(self):
        while True:
            for i in xrange(self._led_count):
                self._led_set(i, 0, 0, 0)
            self.show()
            sleep(0.5)
            for i in xrange(self._led_count):
                self.led_set(i, 255, 255, 255)
            self._show()
            sleep(0.5)

if __name__ == '__main__':
    # Read command-line arguments.
    if len(sys.argv) != 3:
        print 'Usage: ledstripctrl <arduino-usb-port> <led-count>'
    # Name of USB port connected to the Arduino.
    serial_device = sys.argv[1]
    # Number of LED lights on the strip
    led_count = int(sys.argv[2])
    
    # Establish an Arduino connection first.
    print 'Connecting to Arduino...'
    controller = ArduinoController(serial.Serial(serial_device, 115200), led_count)
    time.sleep(2)
    print 'Running'

    # Bring up the cube visualization. Add a call back that sends
    # the cube state to the Arduino.
    c = Cube(3)

    c.draw_interactive(callback=print_cube)
    plt.show()
