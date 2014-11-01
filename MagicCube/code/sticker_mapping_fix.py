'''Fix sticker mapping after we found a bug in our sticker ID assignment.'''
import csv, sys

if __name__ == "__main__":
    # Read command-line arguments.
    if len(sys.argv) != 3:
        print 'Usage: sticker_mapping_fix.py <old-mapping-file> <new-mapping-file>'
        sys.exit(1)
    old_mapping_file = sys.argv[1]
    new_mapping_file = sys.argv[2]

    with open(old_mapping_file, 'rb') as f:
        mapping = dict(((int(items[0]), int(items[1])) for items in csv.reader(f, delimiter=',')))
    
    d = dict(zip(xrange(54), xrange(54)))
    
    old = [44, 41, 38, 43, 40, 37, 42, 39, 36]
    new = [44, 43, 42, 40, 38, 36, 41, 39, 37]
    e = dict(zip(old, new))
    d = dict(d.items() + e.items())
    
    old = [26, 23, 20, 25, 22, 19, 24, 21, 18]
    new = [35, 32, 29, 34, 31, 28, 33, 30, 27]
    e = dict(zip(old, new))
    d = dict(d.items() + e.items())
    
    old = [33, 30, 27, 34, 31, 28, 35, 32, 29]
    new = [24, 21, 18, 25, 22, 19, 26, 23, 20]
    e = dict(zip(old, new))
    d = dict(d.items() + e.items())

    new_mapping = dict(((x, d[y] if y >= 0 else -1)) for x, y in mapping.iteritems())
    with open(new_mapping_file, 'wb') as f:
        for x, y in sorted(new_mapping.iteritems()):
            f.write('%d,%d\n' % (x, y))
