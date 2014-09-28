#!/usr/bin/env python

"""
Show how to connect to keypress events with matplotlib.
"""
from __future__ import print_function
import sys
import numpy as np
import matplotlib.pyplot as plt

def press(event):
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'x':
        xl.set_visible(not xl.get_visible())
        fig.canvas.draw()

fig, ax = plt.subplots()

fig.canvas.mpl_connect('key_press_event', press)

ax.plot(np.random.rand(12), np.random.rand(12), 'go')
xl = ax.set_xlabel('easy come, easy go')

plt.show()
