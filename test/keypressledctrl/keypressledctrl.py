#!/usr/bin/env python
'''
strip.py - Control a strip of LPD8806 driven LEDs in concert with an Arduino program.
Run the ledstripctrl.pde Arduino program before running this script.

Author: Craig Calef <craig@dod.net>
This code is covered under the MIT License
'''

import serial
from msvcrt import getch

SERIAL_DEVICE = 'COM3'  # /dev/cu.usbserial-A900adMy' # Or 'COM3' on my windows machine

if __name__ == '__main__':
    ser = None
    try:
        print 'Connecting to Arduino...'
        ser = serial.Serial(SERIAL_DEVICE, 9600)
        print 'Start pressing keys'
        while True:
            c = getch()
            key = ord(c)
            print 'Pressed', key
            if key == 27:  # ESC
                break
            print 'Sending to Arduino', c
            ser.write(c)
            print 'Read from Arduino:'
            print ser.readline().strip()
        print 'Closing connection'
        ser.close()
    except TypeError as e:
        print 'Error: ', e
        if ser and ser.isOpen():
            print 'Closing connection'
            ser.close()
    print 'Done'
