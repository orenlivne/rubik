'''
============================================================
The Game of Life on a 3x3x3 cube surface.
Created on Apr 22, 2015
@author: Oren Livne <livne@uchicago.edu>
============================================================
'''
import sys, networkx as nx, itertools as it

class GameOfLife(object):
  def __init__(self, g, live):
    # Initializes a game of life on the undirected graph g, starting with the
    # initial configuration whose live cells are the list live.
    # from.
    self._g = g
    self.live = set(live)

  def is_live_at_next_tick(self, u):
    # Returns True if and only the node u is alive at tick t+1 given the state
    # at tick t.
    num_live_nbhrs = sum(1 for v in self._g.neighbors_iter(u) if v in self.live)
    return (num_live_nbhrs == 2 or num_live_nbhrs == 3) if u in self.live else (num_live_nbhrs == 3)

  def tick(self):
    # Advances the state to the next time step (tick).

    # Live cells at next tick = live cells that were live before + live cells that were dead
    # before in neighboring cells of currently live cells
    self.live = set(u for u in self._g if self.is_live_at_next_tick(u)) | \
      set(v for u in self.live for v in self._g.neighbors_iter(u)
          if v not in self.live and self.is_live_at_next_tick(v))

def line_edges(a, b):
  # Returns the list of nearest-neighbor edges between the cells of two 3-cell lines a and b.
  return it.chain(((a[i], b[i + 1]) for i in xrange(2)), ((a[i + 1], b[i]) for i in xrange(2)),
                  ((a[i], a[i + 1]) for i in xrange(2)), ((b[i + 1], b[i]) for i in xrange(2)),
                  ((a[i], b[i]) for i in xrange(3)))

def cube_neighbor_graph(file_name):
  # Builds and returns the 3x3x3 cube Game of Life neighbor graph given a file
  # of line adjacencies.
  with open(file_name, 'rb') as f:
    line, line_prev, edge_list = [], [], []
    for line in (map(int, line.strip().split()) for line in f):
      if line and line_prev:
        for edge in line_edges(line_prev, line): edge_list.append(edge)
      line_prev = line
  return nx.from_edgelist(edge_list, create_using=nx.Graph())

if __name__ == '__main__':
  # Read command-line arguments.
  if len(sys.argv) != 2:
    print 'Usage: nearest_neighbors_graph.py <line-adjacency-list-file>'
    sys.exit(1)
  g = cube_neighbor_graph(sys.argv[1])
  game = GameOfLife(g, [0, 1, 2, 3])
  print game.live
  for _ in xrange(10):
    game.tick()
    print game.live
