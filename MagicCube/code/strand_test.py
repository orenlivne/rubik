#!/usr/bin/env python
'''
strip.py - Control a strip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.ino Arduino program before running this script.

Usage: ledstripctrl <arduino-usb-port> <led-count>

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
'''
import serial, time, sys, ledstripctrl, numpy as np
from functools import partial
import matplotlib.pyplot as plt
from matplotlib import widgets

class StrandtestUi(plt.Axes):
    def __init__(self, controller, fig=None, rect=[0, 0.0, 1, 0.01], **kwargs):
        # Initialize internal state.
        self._controller = controller
        self._led_count = self._controller.led_count
        # Keeps track of the current strip LED light colors.
        self._led = ['000000'] * self._led_count
        # Current LED selected color
        self._rgb = [127, 127, 127]

        if fig is None:
            fig = plt.gcf()
        # disable default key press events
        callbacks = fig.canvas.callbacks.callbacks
        del callbacks['key_press_event']

        # add some defaults, and draw axes
        kwargs.update(dict(aspect=kwargs.get('aspect', 'equal'),
                           xlim=kwargs.get('xlim', (-2.0, 2.0)),
                           ylim=kwargs.get('ylim', (-2.0, 2.0)),
                           frameon=kwargs.get('frameon', False),
                           xticks=kwargs.get('xticks', []),
                           yticks=kwargs.get('yticks', [])))
        super(StrandtestUi, self).__init__(fig, rect, **kwargs)
        self.xaxis.set_major_formatter(plt.NullFormatter())
        self.yaxis.set_major_formatter(plt.NullFormatter())

        self._start_xlim = kwargs['xlim']
        self._start_ylim = kwargs['ylim']

        # Internal state variable
        self._active = False  # true when mouse is over axes
        self._button1 = False  # true when button 1 is pressed
        self._button2 = False  # true when button 2 is pressed
        self._event_xy = None  # store xy position of mouse event
        self._shift = False  # shift key pressed
        self._digit_flags = np.zeros(10, dtype=bool)  # digits 0-9 pressed

#        self._draw_cube()
#        self._execute_cube_callback()

        # connect some GUI events
        self.figure.canvas.set_window_title('LED Strip Control')
        self.figure.canvas.mpl_connect('button_press_event',
                                       self._mouse_press)
        self.figure.canvas.mpl_connect('button_release_event',
                                       self._mouse_release)
        self.figure.canvas.mpl_connect('motion_notify_event',
                                       self._mouse_motion)
        self.figure.canvas.mpl_connect('key_press_event',
                                       self._key_press)
        self.figure.canvas.mpl_connect('key_release_event',
                                       self._key_release)

        self._initialize_widgets()

        # write some instructions
        self.figure.text(0.025, 0.9,
                         "Slide red, green, blue and click LED#\n"
                         "to light an individual LED",
                         size=10)

    def _rgb_string(self):
        return ''.join(map(lambda x: hex(x)[2:].rjust(2,'0'), self._rgb))

    def _initialize_widgets(self):
        self._rgb_text = self.figure.text(0.075, 0.65, "LED color: #" + self._rgb_string())
        self._ax_rgb = self.figure.add_axes([0.3, 0.65, 0.025, 0.025])
        self._btn_rgb = widgets.Button(self._ax_rgb, '')

        x, y, hx = 0.5, 0.9, 0.15
        self._ax_blink = self.figure.add_axes([x, y, hx, 0.075])
        self._btn_blink = widgets.Button(self._ax_blink, 'Blink')
        self._btn_blink.on_clicked(self._blink)

        x += hx
        self._ax_rainbow = self.figure.add_axes([x, y, hx, 0.075])
        self._btn_rainbow = widgets.Button(self._ax_rainbow, 'Rainbow')
        self._btn_rainbow.on_clicked(self._rainbow_cycle)

        x += hx
        self._ax_reset = self.figure.add_axes([x, y, hx, 0.075])
        self._btn_reset = widgets.Button(self._ax_reset, 'Reset')
        self._btn_reset.on_clicked(self._turn_off)
        
        self._slider_ax = [None] * 3
        self._slider = [None] * 3
        for i, label in enumerate(['Red', 'Green', 'Blue']):
            self._slider_ax[i] = plt.axes([0.15, 0.8 - 0.05*i, 0.75, 0.02])
            self._slider[i] = widgets.Slider(self._slider_ax[i], label, 0, 255, valfmt='%d', valinit=127, color='#FF0000')
            self._slider[i].on_changed(partial(self.on_rgb_change, index=i))

        self._ax_led = [None]*self._led_count
        self._btn_led = [None]*self._led_count
        x, y = 0.05, 0.55
        for i in xrange(self._led_count):
            self._ax_led[i] = self.figure.add_axes([x, y, 0.05, 0.05])
            self._btn_led[i] = widgets.Button(self._ax_led[i], '%d' % (i,))
            self._btn_led[i].on_clicked(partial(self.on_led_click, index=i))
            if i % 15 == 14:
                y -= 0.05
                x = 0.05
            else:
                x += 0.05

    def on_led_click(self, event, index):
        rgb = self._rgb_string()
        self._controller.set_led(index, rgb)
        color = '#' + rgb
        self._btn_led[index].color = color
        self._btn_led[index].hovercolor = color
        plt.plot([], [])
        self.figure.canvas.draw()

    def on_rgb_change(self, val, index):
        self._rgb[index] = int(val)
        rgb = self._rgb_string()
        self._rgb_text.set_text( "LED color: #" + rgb)
        color = '#' + rgb
        self._btn_rgb.color = color
        self._btn_rgb.hovercolor = color
        self.figure.canvas.draw()

    def _turn_off(self, *args):
        self._controller.turn_off()

    def _blink(self, *args):
        self._controller.blink(1)

    def _rainbow_cycle(self, *args):
        self._controller.rainbow_cycle()

    def _key_press(self, event):
        """Handler for key press events"""
        if not event.key:
            return 
        elif event.key == 'shift':
            self._shift = True
        elif event.key.isdigit():
            self._digit_flags[int(event.key)] = 1
        elif event.key == 'right':
            pass
        elif event.key == 'left':
            pass
        elif event.key == 'up':
            pass
        elif event.key == 'down':
            pass
        elif event.key.upper() in 'LRUDBF':
            #if self._shift:
            if event.key in 'LRUDBF':
                # Upper-case
                direction = -1
            else:
                # Lower-case
                direction = 1

            N = self.cube.N
            if np.any(self._digit_flags[:N]):
                for d in np.arange(N)[self._digit_flags[:N]]:
                    self.rotate_face(event.key.upper(), direction, layer=d)
            else:
                self.rotate_face(event.key.upper(), direction)
                
#        self._draw_cube()

    def _key_release(self, event):
        """Handler for key release event"""
        if event.key == None:
            return
        if event.key == 'shift':
            self._shift = False
        elif event.key.isdigit():
            self._digit_flags[int(event.key)] = 0

    def _mouse_press(self, event):
        """Handler for mouse button press"""
        self._event_xy = (event.x, event.y)
        if event.button == 1:
            self._button1 = True
        elif event.button == 3:
            self._button2 = True

    def _mouse_release(self, event):
        """Handler for mouse button release"""
        self._event_xy = None
        if event.button == 1:
            self._button1 = False
        elif event.button == 3:
            self._button2 = False

    def _mouse_motion(self, event):
        """Handler for mouse motion"""
        if self._button1 or self._button2:
            dx = event.x - self._event_xy[0]
            dy = event.y - self._event_xy[1]
            self._event_xy = (event.x, event.y)

            if self._button1:
                pass

            if self._button2:
                factor = 1 - 0.003 * (dx + dy)
                xlim = self.get_xlim()
                ylim = self.get_ylim()
                self.set_xlim(factor * xlim[0], factor * xlim[1])
                self.set_ylim(factor * ylim[0], factor * ylim[1])

                self.figure.canvas.draw()

def draw_strandtest_ui(controller):
    # Main call that draws the strand test UI figure.
    fig = plt.figure(figsize=(10, 7))
    fig.add_axes(StrandtestUi(controller))
    return fig

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
        controller = ledstripctrl.LedStripContoller(stream, led_count, debug=0)

        print 'Building UI'
        draw_strandtest_ui(controller)
        plt.show()

        # Shut down strip.
        controller.turn_off()
    except (IOError, OSError):
        # Error or interrupt, shut down strip.
        controller.turn_off()
        sys.exit(141)
