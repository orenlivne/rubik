'''
============================================================
The Game of Life on a graph.
Created on Apr 22, 2015
@author: Oren Livne <livne@uchicago.edu>
============================================================
'''
import sys, networkx as nx, itertools as it, random, time

class GameOfLife(object):
  def __init__(self, g, live):
    # Initializes a game of life on the undirected graph g, starting with the
    # initial configuration whose live cells are the list live.
    # from.
    self._g = g
    # live = dictionary of live cell-location-to-cell-age.
    self.live = dict((u, 1) for u in live)

  def is_live_at_next_tick(self, u):
    # Returns True if and only the node u is alive at tick t+1 given the state
    # at tick t.
    num_live_nbhrs = sum(1 for v in self._g.neighbors_iter(u) if v in self.live)
    return (num_live_nbhrs == 2 or num_live_nbhrs == 3) if u in self.live else (num_live_nbhrs == 3)

  def tick(self):
    # Advances the state to the next time step (tick).

    # Live cells at next tick = live cells that were live before + live cells that were dead
    # before in neighboring cells of currently live cells
    self.live = dict(it.chain(((u, age+1) for u, age in self.live.iteritems()
                               if self.is_live_at_next_tick(u)),
                              ((v, 1) for u in self.live for v in self._g.neighbors_iter(u)
                               if v not in self.live and self.is_live_at_next_tick(v))))

if __name__ == '__main__':
  # Read command-line arguments.
  if len(sys.argv) != 2:
    print 'Usage: game_of_life.py <neighbors-graph-pickle-file>'
    sys.exit(1)
  g = nx.read_gpickle(sys.argv[1])

  while True:
    initial_population_size = random.randint(int(0.1 * g.number_of_nodes()), g.number_of_nodes())
    print 'Initial population size', initial_population_size
    initial_population = random.sample(g.nodes(), initial_population_size)
    game = GameOfLife(g, initial_population)
    print game.live
    time.sleep(0.3)
    for tick in xrange(100):
      game.tick()
      print tick, ' '.join(map(str, sorted(game.live.iteritems())))
      time.sleep(0.3)
      # Stop simulation on extinction.
      if not game.live: break
