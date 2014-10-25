#!/usr/bin/env python
'''
strip.py - Control a MagicCube integrated with astrip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.ino Arduino program before running this script.

Usage: ledstripctrl <arduino-usb-port> <led-count>

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
'''

import serial, time, sys, ledstripctrl
import matplotlib.pyplot as plt
from cube_interactive import Cube

'''Integrates MagicCube with the LED strip. Sends the cube state
to the LED strip upon a call to send_cube_state().'''
class CubeLedStripContoller(ledstripctrl.LedStripContoller):
    def __init__(self, serial_stream, led_count, face_colors, debug=False):
        ledstripctrl.LedStripContoller.__init__(self, serial_stream, led_count, debug=debug)
        self.face_colors = map(lambda x: (x[1:] if x.startswith('#') else x).upper(), face_colors)

    def send_cube_state(self, sticker_color_id):
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
    # Cube face colors. Each color must be in 6-letter uppercase hex format.
    # These are displayed on the screen.
    display_face_colors = ['#ffffff', '#ffcf00',
                           '#00008f', '#009f0f',
                           '#ff6f00', '#cf0000']
    # These are displayed on the LED strip.
    strip_face_colors = ['#ffffff', '#ffff00',
                         '#0000ff', '#00cf00',
                         '#6d1200', '#ff0000']

    # Cube dimension.
    N = 3
    
    try:
        # Establish an Arduino connection first.
        print 'Connecting to Arduino...'
        stream = serial.Serial(serial_device, 115200)
        time.sleep(2)

        # Start LED controller.
        print 'Starting controller'
        controller = CubeLedStripContoller(stream, led_count, strip_face_colors, debug=1)
    
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
