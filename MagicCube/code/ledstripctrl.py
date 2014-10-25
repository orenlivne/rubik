#!/usr/bin/env python
'''
strip.py - Control a strip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.ino Arduino program before running this script.

Usage: ledstripctrl <arduino-usb-port> <led-count>

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
'''
import serial, time, sys, readline

class LedStripContoller(object):
    '''A generic controller of a digital LED strip via a USB stream.''' 
    def __init__(self, serial_stream, led_count, debug=0):
        self._serial_stream = serial_stream
        self.led_count = led_count
        self._debug = debug
        self.turn_off()
            
    def set_uniform_color(self, color):
        '''Set a uniform color to all LEDs.'''
        for i in xrange(self.led_count):
            self._led_set(i, color)
        self._show()

    def set_led(self, led, rgb):
        # Set a single led to the color rgb.
        self._led_set(led, rgb)
        self._show()

    def turn_off(self):
        '''Turn the strip off.'''
        self.set_uniform_color('000000')
    
    def blink(self, num_blinks, blink_time=0.25, color='FFFFFF'):
        for _ in xrange(num_blinks):
            self.turn_off()
            # self._show()
            time.sleep(blink_time)
            
            self.set_uniform_color(color)
            # self._show()
            time.sleep(blink_time)
        self.turn_off()

    def rainbow_cycle(self, num_cycles=5, delay=0):
        '''Makes a rainbow wheel that is equally distributed along the chain.'''
        num_colors = 384
        for j in xrange(1): #xrange(num_colors * num_cycles):  # n cycles of all 384 colors in the wheel
            for i in xrange(self.led_count):
                # tricky math! we use each pixel as a fraction of the full 384-color wheel
                # (thats the i / strip.numPixels() part)
                # Then add in j which makes the colors go around per pixel
                # the % 384 is to make the wheel cycle around
                r, g, b = self._wheel(((i * num_colors / self.led_count) + j) % num_colors)
                self._led_set(i, '%02X%02X%02X' % (r, g, b))
            self._show()
            time.sleep(delay)

    def _flush_read_buffer(self):
        data_from_arduino = self._serial_stream.readline().strip()
        if self._debug >= 2:
            print data_from_arduino
    
    def _show(self):
        self._serial_stream.write('FF\n')
        self._flush_read_buffer()
    
    def _led_set(self, led, rgb):
        outval = '%02X%0s' % (led, rgb)
        if self._debug >= 1:
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
    
if __name__ == '__main__':
    # Read command-line arguments.
    if len(sys.argv) != 3:
        print 'Usage: ledstripctrl <arduino-usb-port> <led-count>'
        sys.exit(1)
    # Name of USB port connected to the Arduino.
    serial_device = sys.argv[1]
    # Number of LED lights on the strip.
    led_count = int(sys.argv[2])
    
    try:
        # Establish an Arduino connection first.
        print 'Connecting to Arduino...'
        stream = serial.Serial(serial_device, 115200)
        time.sleep(2)

        # Start LED controller.
        print 'Starting controller'
        controller = LedStripContoller(stream, led_count, debug=1)
        
        # Run a strip test.
        print 'Blink test'
        controller.blink(1, time=0.1)

        # Shut down strip.
        controller.turn_off()
    except (IOError, OSError):
        # Error or interrupt, shut down strip.
        controller.turn_off()
        sys.exit(141)
