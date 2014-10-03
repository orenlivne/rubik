#!/usr/bin/env python
'''
strip.py - Control a strip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.ino Arduino program before running this script.

Usage: ledstripctrl <arduino-usb-port> <led-count>

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
'''

import serial, time, sys
import matplotlib.pyplot as plt
from time import sleep
from MagicCube.code.cube_interactive import Cube

'''A generic controller of a digital LED strip via a USB stream.''' 
class LedStripContoller(object):
    def __init__(self, serial_stream, led_count):
        self._serial_stream = serial_stream
        self._led_count = led_count
            
    def blink_test(self, num_blinks):
        for _ in xrange(num_blinks):
            self.turn_off()
            #self._show()
            sleep(0.5)
            
            self.set_uniform_color('FFFFFF')
            #self._show()
            sleep(0.5)
        self.turn_off()
    
    # Set a uniform color to all LEDs.
    def set_uniform_color(self, color):
        for i in xrange(self._led_count):
            self._led_set(i, color)
        self._show()

    # Turn the strip off.
    def turn_off(self):
        self.set_uniform_color('000000')
    
    def _clear_read_buffer(self):
        print self._serial_stream.readline().strip()
    
    def _show(self):
        self._serial_stream.write('FF\n')
        print self._serial_stream.readline()
    
    def _led_set(self, led, rgb):
        outval = '%02X%0s' % (led, rgb)
        print outval
        self._serial_stream.write('%s\n' % outval)
        print self._serial_stream.readline()

'''Integrates MagicCube with the LED strip. Sends the cube state
to the LED strip upon a call to send_cube_state().'''
class CubeLedStripContoller(LedStripContoller):
    def __init__(self, serial_stream, led_count, face_colors):
        LedStripContoller.__init__(self, serial_stream, led_count)
        self.face_colors = map(lambda x: (x[1:] if x.startswith('#') else x).upper(), face_colors)

    def send_cube_state(self, sticker_color_id):
        print ' '.join(repr(y) for y in sticker_color_id)
        for i in xrange(min(led_count, len(sticker_color_id))):
            self._led_set(i, self.face_colors[sticker_color_id[i]])
            self._show()
        
if __name__ == '__main__':
    # Read command-line arguments.
    if len(sys.argv) != 3:
        print 'Usage: ledstripctrl <arduino-usb-port> <led-count>'
        sys.exit(1)
    # Name of USB port connected to the Arduino.
    serial_device = sys.argv[1]
    # Number of LED lights on the strip.
    led_count = int(sys.argv[2])
    # Cube face colors. Must be in 6-letter uppercase hex format.
    face_colors = ['#ffffff', '#ffcf00',
                   '#00008f', '#009f0f',
                   '#ff6f00', '#cf0000',
                   'gray', 'none']  # Unclear what those last two colors are.
    # Cube dimension.
    N = 3
    
    try:
        # Establish an Arduino connection first.
        print 'Connecting to Arduino...'
        stream = serial.Serial(serial_device, 115200)
        time.sleep(2)
        print 'Starting controller'
        controller = CubeLedStripContoller(stream, led_count, face_colors[:2 * N])
        #controller.blink_test(N)
    
        # Bring up the cube visualization. Add a call back that sends
        # the cube state to the Arduino.
        c = Cube(N, face_colors=face_colors)
        c.draw_interactive(callback=controller.send_cube_state)
        plt.show()
        controller.turn_off()
    except (IOError, OSError):
        controller.turn_off()
        sys.exit(141)
