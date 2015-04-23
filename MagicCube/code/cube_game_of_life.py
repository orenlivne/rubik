# Matplotlib Game of Life simulator on a Rubik's cube surface.
# Adapted from cube code written by David Hogg
#   https://github.com/davidwhogg/MagicCube

import numpy as np, itertools as it, matplotlib.pyplot as plt, sys, networkx as nx, random
from matplotlib import widgets
# from MagicCube.code.projection import Quaternion, project_points
from projection import Quaternion, project_points
from cube_interactive import Cube
from game_of_life import GameOfLife

class GameOfLifeGui(plt.Axes):
    def __init__(self, cube=None,
                 interactive=True,
                 view=(0, 0, 10),
                 fig=None, rect=[0, 0.16, 1, 0.84],
                 max_ticks=100,
                 simulation_interval_msecs=500,
                 callback=None,
                 **kwargs):
        # Game of Life simulation controls.
        self._max_ticks = max_ticks
        self._simulation_interval_msecs = simulation_interval_msecs
        self._init_simulation()

        # Optional call-back that receives the cube state whenever it is updated.
        self.callback = callback
        if cube is None:
            self.cube = Cube(3)
        elif isinstance(cube, Cube):
            self.cube = cube
        else:
            self.cube = Cube(cube)

        self._view = view
        self._start_rot = Quaternion.from_v_theta((1, -1, 0),
                                                  - np.pi / 6)

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
        super(GameOfLifeGui, self).__init__(fig, rect, **kwargs)
        self.xaxis.set_major_formatter(plt.NullFormatter())
        self.yaxis.set_major_formatter(plt.NullFormatter())

        self._start_xlim = kwargs['xlim']
        self._start_ylim = kwargs['ylim']

        # Define movement for up/down arrows or up/down mouse movement
        self._ax_UD = (1, 0, 0)
        self._step_UD = 0.01

        # Define movement for left/right arrows or left/right mouse movement
        self._ax_LR = (0, -1, 0)
        self._step_LR = 0.01

        self._ax_LR_alt = (0, 0, 1)

        # Internal state variable
        self._active = False  # true when mouse is over axes
        self._button1 = False  # true when button 1 is pressed
        self._button2 = False  # true when button 2 is pressed
        self._event_xy = None  # store xy position of mouse event
        self._shift = False  # shift key pressed
        self._digit_flags = np.zeros(10, dtype=bool)  # digits 0-9 pressed

        self._current_rot = self._start_rot  # current rotation state
        self._face_polys = None
        self._sticker_polys = None

        self._draw_cube()
        self._execute_cube_callback()

        # connect some GUI events
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
        self._simulation_id = None
        self.figure.canvas.mpl_connect('draw_event',
                                       self._start_simulation_timer)
        self._initialize_widgets()

        # write some instructions
        self.figure.text(0.05, 0.05,
                         "Mouse/arrow keys adjust view\n"
                         "Up/Down keys to adjust simulation speed",
                         size=10)

    def _initialize_widgets(self):
        self._ax_quit = self.figure.add_axes([0.8, 0.05, 0.15, 0.075])
        self._btn_quit = widgets.Button(self._ax_quit, 'Quit')
        self._btn_quit.on_clicked(self._quit)

    def _start_simulation_timer(self, event):
        # Create a new timer object. Set the interval to self._simulation_interval_msecs
        # milliseconds (1000 is default) and tell the timer what function should be called.
        if self._simulation_id is not None:
            self.fig.canvas.mpl_disconnect(self._simulation_id)
        self._timer = fig.canvas.new_timer(interval=self._simulation_interval_msecs)
        self._simulation_id = self._timer.add_callback(self._run_simulation, self)
        self._timer.start()

    def _quit(self, *args):
        plt.close()

    def _project(self, pts):
        return project_points(pts, self._current_rot, self._view, [0, 1, 0])

    def _execute_cube_callback(self):
        if self.callback:
            self.callback(self.cube.color_id())

    def _draw_cube(self):                
        stickers = self._project(self.cube._stickers)[:, :, :2]
        faces = self._project(self.cube._faces)[:, :, :2]
        face_centroids = self._project(self.cube._face_centroids[:, :3])
        sticker_centroids = self._project(self.cube._sticker_centroids[:, :3])

        plastic_color = self.cube.plastic_color
        colors = np.asarray(self.cube.face_colors)[self.cube._colors]
        face_zorders = -face_centroids[:, 2]
        sticker_zorders = -sticker_centroids[:, 2]

        if self._face_polys is None:
            # initial call: create polygon objects and add to axes
            self._face_polys = []
            self._sticker_polys = []

            for i in xrange(len(colors)):
                fp = plt.Polygon(faces[i], facecolor=plastic_color,
                                 zorder=face_zorders[i])
                sp = plt.Polygon(stickers[i], facecolor=colors[i],
                                 zorder=sticker_zorders[i])

                self._face_polys.append(fp)
                self._sticker_polys.append(sp)
                self.add_patch(fp)
                self.add_patch(sp)
        else:
            # subsequent call: update the polygon objects
            for i in xrange(len(colors)):
                self._face_polys[i].set_xy(faces[i])
                self._face_polys[i].set_zorder(face_zorders[i])
                self._face_polys[i].set_facecolor(plastic_color)

                self._sticker_polys[i].set_xy(stickers[i])
                self._sticker_polys[i].set_zorder(sticker_zorders[i])
                self._sticker_polys[i].set_facecolor(colors[i])

        self.figure.canvas.draw()

    def rotate(self, rot):
        self._current_rot = self._current_rot * rot

    def rotate_face(self, face, turns=1, layer=0, steps=5, execute_call_back=True):
        if not np.allclose(turns, 0):
            for _ in xrange(steps):
                self.cube.rotate_face(face, turns * 1. / steps, layer=layer)
                self._draw_cube()
            if execute_call_back:
                self._execute_cube_callback()

    def _reset_view(self, *args):
        self.set_xlim(self._start_xlim)
        self.set_ylim(self._start_ylim)
        self._current_rot = self._start_rot
        self._draw_cube()

    def _randomize_cube(self, *args):
        # Reset the cube.
        self.set_xlim(self._start_xlim)
        self.set_ylim(self._start_ylim)
        self._current_rot = self._start_rot

        # Perform a sequence of random moves.
        layer = 0
        for _ in xrange(15):
            face = GameOfLifeGui.FACES[np.random.randint(2 * self.cube.N)]
            n = np.random.randint(4)
            self.rotate_face(face, n, layer, steps=3, execute_call_back=False)
        self._draw_cube()
        self._execute_cube_callback()

    def _key_press(self, event):
        """Handler for key press events"""
        if not event.key:
            return 
        if event.key == 'up':
            print 'up'
        elif event.key == 'down':
            print 'down'

    def _key_release(self, event):
        """Handler for key release event"""
        if event.key == None:
            return
        if event.key == 'shift':
            self._shift = False

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
                if self._shift:
                    ax_LR = self._ax_LR_alt
                else:
                    ax_LR = self._ax_LR
                rot1 = Quaternion.from_v_theta(self._ax_UD,
                                               self._step_UD * dy)
                rot2 = Quaternion.from_v_theta(ax_LR,
                                               self._step_LR * dx)
                self.rotate(rot1 * rot2)

                self._draw_cube()

            if self._button2:
                factor = 1 - 0.003 * (dx + dy)
                xlim = self.get_xlim()
                ylim = self.get_ylim()
                self.set_xlim(factor * xlim[0], factor * xlim[1])
                self.set_ylim(factor * ylim[0], factor * ylim[1])

                self.figure.canvas.draw()

    def _init_simulation(self):
        # Restart a new Game of Life simulation.
        initial_population_size = random.randint(int(0.1 * g.number_of_nodes()), g.number_of_nodes())
        print 'Initial population size', initial_population_size
        initial_population = random.sample(g.nodes(), initial_population_size)
        self._game = GameOfLife(g, initial_population)
        self._tick = -1

    def _run_simulation(self, *args):
        # Restart simulation on extinction or after the max # of timesteps has been reached.
        if self._tick == self._max_ticks or not self._game.live:
            self._init_simulation()
        self._tick += 1
        print 'Tick', self._tick, 'live cells', ' '.join(map(str, sorted(self._game.live.iteritems())))

def print_cube(sticker_color_id):
    print ' '.join(repr(y) for y in sticker_color_id)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: cube_game_of_life.py <neighbors-graph-pickle-file>'
        sys.exit(1)
    g = nx.read_gpickle(sys.argv[1])
    face_colors = ["white", "yellow",
                 "blue", "green",
                 "purple", "red",
                 "gray", "none"]    
    c = Cube(3, face_colors=face_colors)
    fig = plt.figure(figsize=(7, 5))
    fig.add_axes(GameOfLifeGui(c, callback=print_cube))
    plt.show()
