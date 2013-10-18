from datetime import datetime
from math import pow
from PIL import Image, ImageDraw
import random

VERBOSE = False
DEBUG = False

def p_norm(p1, p2, p):
    if p == 'inf' or p == float('inf'):
        return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))
    return pow(abs(p1[0] - p2[0])**p + abs(p1[1] - p2[1])**p, 1.0/p)

def euclidian(p1, p2):
    return p_norm(p1, p2, 2)

def manhattan(p1, p2):
    return p_norm(p1, p2, 1)
    
def chessboard(p1, p2): #chessboard/chebyshev distance; maximum/L-inf norm; what-have-you
    return p_norm(p1, p2, 'inf')

def voronoi_diagram(width, height, cells=None, num_cells=20, metric=euclidian, save=False):
    img = Image.new("RGB", (width, height))
    if cells is None:
        cells = [(random.randrange(width), random.randrange(height)) for n in range(num_cells)]
    colors = [(random.randrange(256), random.randrange(256), random.randrange(256)) for e in cells]
    for y in range(height):
        for x in range(width):
            min_dist = euclidian((0,0), (width - 1, height - 1))
            j = 0
            for i, e in enumerate(cells):
                cell_dist = metric(e, (x, y))
                if cell_dist < min_dist:
                    min_dist = cell_dist
                    j = i
            img.putpixel((x,y), colors[j])
    for e in cells:
        spacing = 5
        draw = ImageDraw.Draw(img)
        draw.rectangle((e[0] - spacing, e[1] - spacing, e[0] + spacing, e[1] + spacing), fill=(0,0,0))
        if DEBUG:
            draw.text((e[0] - 10, e[1] + 6), str(e))
        del draw
    if save:
        now = datetime.now()
        if VERBOSE:
            print 'Saving to "%s-%s.png"' % (metric.__name__.upper(), now)
	    img.save('%s-%s.png' % (metric.__name__.upper(), now), 'PNG')
    else:
        img.show()

def voronoi_diagram_for_multi_metrics(width, height, metrics, cells=None, num_cells=None, save=False):
    if cells is None and num_cells is None:
        raise ValueError("No cell points nor number of points to generate provided.")
    if num_cells is not None and cells is None:
        if VERBOSE:
            print 'Generating %s points...' % num_cells
        cells = [(random.randrange(width), random.randrange(height)) for n in range(num_cells)]
    for metric in metrics:
        if VERBOSE:
            print 'Creating Voronoi diagram with the %s metric...' % metric.__name__.upper()
        voronoi_diagram(width, height, cells=cells, metric=metric, save=save)

def parse_file(f, delimiter=' '):
    if VERBOSE:
        print 'Reading data file %s...' % f
    f = open(f, 'r')
    cells = []
    for line in f.readlines():
        fld = line.split(delimiter)
        x = float(fld[0])
        y = float(fld[1])
        cells.append((x,y))
    f.close()
    return cells

def main(args):
    if args.V:
        print 'Running in verbose mode...'
        global VERBOSE
        VERBOSE = True #Bug: won't save unless in verbose mode for whatever reason

    metric_dict = {'all': None, 'euclidian': euclidian, 'manhattan': manhattan, 'chessboard': chessboard}
    metric = metric_dict[args.M.lower()]
    
    num_cells = 20
    if args.N is not None:
        num_cells = args.N

    cells = None
    if args.file is not None:
        cells = parse_file(args.file)
    
    if metric is not None:
        voronoi_diagram(args.W, args.H, cells=cells, num_cells=num_cells, metric=metric, save=args.S)
    else:
        del metric_dict['all']
        metrics = metric_dict.values()
        voronoi_diagram_for_multi_metrics(args.W, args.H, metrics, cells=cells, num_cells=num_cells, save=args.S)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-W', type=int, help='Width of window', default=500)
    parser.add_argument('-H', type=int, help='Height of window', default=500)
    parser.add_argument('-N', type=int, help='Number of cells', default=20)
    parser.add_argument('-C', dest='file', metavar='FILE', help='File containing space delimited lines of coordiantes. Takes precedence over the -n arg.', default=None)
    parser.add_argument('-S', action='store_true', help='Save the files', default=False)
    parser.add_argument('-M', type=str, help='Metric type. Current Avaliable Options:\Chessboard\nEuclidian\nManhattan\nAll', default='euclidian')
    parser.add_argument('-V', action='store_true', help='Enable verbose mode', default=False)
    args = parser.parse_args()
    main(args)