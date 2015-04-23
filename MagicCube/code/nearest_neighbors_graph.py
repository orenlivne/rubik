'''Build the nearest neighbor Game of Life graph on the surface of a cube from a file
containing groups of lines. Within each group, each two consecutive lines are connected
(8-neighbor pattern.'''
import sys, networkx as nx, itertools as it
from collections import Counter

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

if __name__ == "__main__":
  # Read command-line arguments.
  if len(sys.argv) != 3:
    print 'Usage: nearest_neighbors_graph.py <line-adjacency-list-file> <output-pickle-file>'
    sys.exit(1)

  g = cube_neighbor_graph(sys.argv[1])
  for node in g:
    print 'sticker', node, 'degree', g.degree(node), sorted(g.neighbors(node))
  print 'Degree frequencies', Counter(g.degree(node) for node in g)
  nx.write_gpickle(g, sys.argv[2])
