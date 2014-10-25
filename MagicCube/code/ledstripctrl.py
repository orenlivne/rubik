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
#from MagicCube.code.cube_interactive import Cube
from cube_interactive import Cube

class LedStripContoller(object):
    '''A generic controller of a digital LED strip via a USB stream.''' 
    def __init__(self, serial_stream, led_count, debug=False):
        self._serial_stream = serial_stream
        self._led_count = led_count
        self._debug = debug
        self.turn_off()
            
    def set_uniform_color(self, color):
        '''Set a uniform color to all LEDs.'''
        for i in xrange(self._led_count):
            self._led_set(i, color)
        self._show()

    def turn_off(self):
        '''Turn the strip off.'''
        self.set_uniform_color('000000')
    
    def blink_test(self, num_blinks, color='FFFFFF'):
        for _ in xrange(num_blinks):
            self.turn_off()
            # self._show()
            sleep(0.5)
            
            self.set_uniform_color(color)
            # self._show()
            sleep(0.5)
        self.turn_off()

    def rainbow_cycle(self, num_cycles=5, delay=0):
        '''Makes a rainbow wheel that is equally distributed along the chain.'''
        num_colors = 384
        for j in xrange(1):  # xrange(num_colors * num_cycles):  # n cycles of all 384 colors in the wheel
            for i in xrange(self._led_count):
                # tricky math! we use each pixel as a fraction of the full 384-color wheel
                # (thats the i / strip.numPixels() part)
                # Then add in j which makes the colors go around per pixel
                # the % 384 is to make the wheel cycle around
                r, g, b = self._wheel(((i * num_colors / self._led_count) + j) % num_colors)
                self._led_set(i, '%02X%02X%02X' % (r, g, b))
            self._show()
            time.sleep(delay)

    def _flush_read_buffer(self):
        data_from_arduino = self._serial_stream.readline().strip()
        if self._debug:
            print data_from_arduino
    
    def _show(self):
        self._serial_stream.write('FF\n')
        self._flush_read_buffer()
    
    def _led_set(self, led, rgb):
        outval = '%02X%0s' % (led, rgb)
        print 'Setting LED %d to %s (outval=%s)' % (led, rgb, outval)
        self._serial_stream.write('%s\n' % outval)
        self._flush_read_buffer()

    '''Returns an RGB color value for a color identifier between 0 and 384.
    Colors are a transition r - g -b - back to r.'''
    def _wheel(self, wheel_pos):
        q = wheel_pos / 128
        if q == 0:
            r = 127 - wheel_pos % 128  # Red down
            g = wheel_pos % 128  # green up
            b = 0  # blue off
        elif q == 1:
            g = 127 - wheel_pos % 128  # green down
            b = wheel_pos % 128  # blue up
            r = 0  # red off
        elif q == 2:
            b = 127 - wheel_pos % 128  # blue down 
            r = wheel_pos % 128  # red up
            g = 0  # green off
        return r, g, b
    
'''Integrates MagicCube with the LED strip. Sends the cube state
to the LED strip upon a call to send_cube_state().'''
class CubeLedStripContoller(LedStripContoller):
    def __init__(self, serial_stream, led_count, face_colors, debug=False):
        LedStripContoller.__init__(self, serial_stream, led_count, debug=debug)
        self.face_colors = map(lambda x: (x[1:] if x.startswith('#') else x).upper(), face_colors)

    def send_cube_state(self, sticker_color_id):
        print face_colors
        print ' '.join(repr(y) for y in sticker_color_id)
        for i in xrange(min(led_count, len(sticker_color_id))):
            print 'Sticker %d: color %s' % (i, self.face_colors[sticker_color_id[i]])
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
        controller = CubeLedStripContoller(stream, led_count, face_colors[:2 * N], debug=True)
        # Test how face colors appear on the LED strip.
#         for x in face_colors[:6]:
#             controller.set_uniform_color(x[1:])
#             time.sleep(3)
        controller.set_uniform_color('FFFFFF')
        time.sleep(1000)
        controller.rainbow_cycle(5, 0)
        time.sleep(2)
        controller.turn_off()
                
        # input('Press ENTER to continue.')
        # controller.blink_test(N, color='#ff0000')
    
        # Bring up the cube visualization. Add a call back that sends
        # the cube state to the Arduino.
        c = Cube(N, face_colors=face_colors)
        c.draw_interactive(callback=controller.send_cube_state)
        plt.show()
        controller.turn_off()
    except (IOError, OSError):
        controller.turn_off()
        sys.exit(141)
