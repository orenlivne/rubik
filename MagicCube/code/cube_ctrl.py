#!/usr/bin/env python
'''
strip.py - Control a MagicCube integrated with astrip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.ino Arduino program before running this script.

Usage: ledstripctrl <arduino-usb-port> <led-count>

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
'''

import serial, time, sys, ledstripctrl, csv
import matplotlib.pyplot as plt
from cube_interactive import Cube

'''Integrates MagicCube with the LED strip. Sends the cube state
to the LED strip upon a call to send_cube_state().'''
class CubeLedStripContoller(ledstripctrl.LedStripContoller):
    # Color of an LED that's turned off.
    COLOR_OFF = '#000000'

    def __init__(self, serial_stream, led_to_sticker_mapping, face_colors, debug=False):
        self.debug = debug
        self.led_to_sticker_mapping = led_to_sticker_mapping
        self.led_count = max(led_to_sticker_mapping.iterkeys()) + 1
        print 'LED count is ' + repr(self.led_count)
        ledstripctrl.LedStripContoller.__init__(self, serial_stream, self.led_count, debug=debug)
        self.face_colors = map(lambda x: (x[1:] if x.startswith('#') else x).upper(), face_colors)

    def send_cube_state(self, sticker_color_id):
        # Light each LED with the color of the corresponding sticker.
        print ' '.join(repr(y) for y in sticker_color_id)
        for led, sticker_id in self.led_to_sticker_mapping.iteritems():
            color = self.face_colors[sticker_color_id[sticker_id]] if sticker_id >= 0 else CubeLedStripContoller.COLOR_OFF
            if self.debug >= 1:
                print 'LED %d, sticker %d, color %s' % (led, sticker_id, color)
            self._led_set(led, color)
            self._show()

def load_led_to_sticker_mapping(data):
    # Load a comma-separated file with LED#,sticker# data. -1 sticker# indicates that the light
    # should stay off. LED#, sticker# are 0-based.
    return dict((int(items[0]), int(items[1])) for items in csv.reader(data, delimiter=','))
        
if __name__ == '__main__':
    # Read command-line arguments.
    if len(sys.argv) != 3:
        print 'Usage: ledstripctrl <arduino-usb-port> <led-to-sticker-mapping-file>'
        sys.exit(1)
    # Name of USB port connected to the Arduino.
    serial_device = sys.argv[1]
    # Number of LED lights on the strip.
    with open(sys.argv[2], 'rb') as mapping_file:
        led_to_sticker_mapping = load_led_to_sticker_mapping(mapping_file)
        print led_to_sticker_mapping

    # Cube face colors. Each color must be in 6-letter uppercase hex format.
    # These are displayed on the screen.
    display_face_colors = ['#ffffff', '#ffcf00',
                           '#0000ff', '#009f0f',
                           '#ff00ff', '#cf0000']
    # These are displayed on the LED strip.
    strip_face_colors = ['#ffffff', '#ffff00',
                         '#0000ff', '#00cf00',
                         '#50002f', '#ff0000']

    # Cube dimension.
    N = 3
    
    try:
        # Establish an Arduino connection first.
        print 'Connecting to Arduino...'
        stream = serial.Serial(serial_device, 115200)
        time.sleep(2)

        # Start LED controller.
        print 'Starting controller'
        controller = CubeLedStripContoller(stream, led_to_sticker_mapping, strip_face_colors, debug=0)
    
        # Bring up the cube visualization. Add a call back that sends
        # the cube state to the Arduino.
        c = Cube(N, face_colors=display_face_colors + ['gray', 'none'])  # Unclear what those last two colors are used for.
        c.draw_interactive(callback=controller.send_cube_state)
        plt.show()

        # Visualization was exited, shut down LED strip and serial port.
        controller.turn_off()
    except (IOError, OSError):
        # Error or CTRL-C was pressed, shut down LED strip and serial port.
        controller.turn_off()
        sys.exit(141)
