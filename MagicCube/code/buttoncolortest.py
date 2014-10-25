import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import itertools


fig, ax = plt.subplots()
button = Button(ax, 'Click me!')

colors = itertools.cycle(['red', 'green', 'blue'])

def change_color(event):
    button.color = next(colors)
    # If you want the button's color to change as soon as it's clicked, you'll
    # need to set the hovercolor, as well, as the mouse is still over it
    button.hovercolor = button.color
    fig.canvas.draw()

button.on_clicked(change_color)

plt.show()
