#!/usr/bin/env python

import cv
import cv2

from math import pi, sqrt
from numpy import array, dot
from numpy.linalg import pinv

from optparse import OptionParser

import os
import sys

def usage():
    print '''
            lines.py - given an image, attempt to find the apparent straight lines in it.

            USAGE: python lines.py -i file [-c file]
                   ./lines.py -i file -[c s v p]
            
                   -c attempts to connect the coherent line segments in the image to a single line
                   -p attempts to find the 3D ground plane point cloud
                   -s saves the new image to 'line_detection.jpg'
                   -v sets verbosity to True
          '''

#White line finding methods
def dist(line1, line2):
    '''
        Finds Euclidian distance between last point of line1 and first point of line2.
    '''
    return sqrt((line1[2] - line2[0]) ** 2 + (line1[3] - line2[1]) ** 2)

def find_lines(img):
    '''
        Finds line or line-like structures in the given img by use of cv2.Canny and cv2.HoughLines
    '''
    newimg = cv2.GaussianBlur(img, (7,7), 0)
    c = cv2.Canny(newimg, 75, 125)#275)
    lines = cv2.HoughLinesP(c, 1, pi/180, 60)
    f = open('lines.txt', 'w')
    for l in lines[0]:
        f.writelines(str(l) + '\n')
    f.close()
    return lines[0]

def connect_lines(lines):
    '''
        Connects the lines from the find_lines function to be more contiguous.
        Currently not very time efficient, and no pruning is done. (Not recommended for use.) 
    '''
    new_lines = []
    a = 0
    for l1 in lines:
        for l2 in lines:
            d = dist(l1, l2)
            if d < 10 and d != 0:
                new_lines.append((l1[0], l1[1], l2[2], l2[3]))
            a+=1
            if a % 500000 == 0: print 'Iterations:', a
    return new_lines

def projection(lines, Pinv):
    '''
        Finds the projection of the lines (converted to 3-space) into 4-space given a Pose matrix Pinv.
        Arguments:
            'lines' - collection of lines represented by lists of their start and endpoints in 3D space.
            'Pinv' - pseudo-inverse of our original camera pose matrix.
    '''
    four_space = []
    for line in lines:
        four_space.append(dot(Pinv, line))
    return four_space

def three_space(lines):
    '''
        Converts given points into three space.
    '''
    points = []
    for line in lines:
        points.append([line[0], line[1], 1])
        points.append([line[2], line[3], 1])
    return points

def find_ground_plane(lines, P):
    '''
        Attempts to find the ground plane points from the points of 'lines' and camera pose matrix P using the equation:
            X(t) = (P^(-1)*(t*x - p_4), 1)^T.

        Arguments:
            lines - collection of lines represented by lists of their start and endpoints in 2D Euclidian space.
            P - 3x4 camera pose matrix

        Notes:
            P^-1 can be estimated by the pseudoinverse of P.
            t is given by ((p0 - l0).n)/(l.n) where l is a vector on our line, l0 is a point on the line, and n is the normal vector to the plane.
            x is the homogenous coordinate from the projection.
            p_4 is fourth column in P.
    '''

    p4 = array([P[0][-1], P[1][-1], P[2][-1]])
    p0 = array([0, 0, 0, 1])
    n = array([0, 0, 1, 0])

    #convert lines to 3-space
    xs = three_space(lines)

    #pseudoinverse
    Pinv = pinv(P)

    #projections
    projs = projection(xs, Pinv)
    
    #hopefully my math is correct :P
    f = open('plane_points.txt', 'w')
    for x, X in map(None, xs, projs):
        x = array(x) #3x1
        l = array(X) #4x1
        t = dot(p0 - l, n) / dot(l, n)
        new_X = dot(Pinv, (t*x - p4))
        #print new_X
        f.write('%s\n' % new_X)
    f.close()
    
def draw_lines(img, do_connect, save, verbose, plane):

    print 'Tasks:\n Drawing lines - True\n Connecting lines - %s\n Finding ground plane - %s\n Saving to disk - %s' % (do_connect, plane, save)

    newimg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if verbose: print 'Attempting to find lines'
    found_lines = find_lines(newimg)

    if plane:
        if verbose: 'Attempting to find ground plane'
        P = array([[1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0], [0.5, 1.0, 1.5, 2.0]]) #make up stuff for now
        find_ground_plane(found_lines, P)

    if verbose: print 'Total lines:', len(found_lines)
    if do_connect:
        found_lines = connect_lines(found_lines)
        if verbose: print 'Connected Lines:', len(connected_lines)
    
    if verbose: print 'Drawing lines'
    for l in found_lines:
        x1, y1, x2, y2 = l
        cv.Line(cv.fromarray(img), (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
    
    cv2.imshow('Line Detection Test', img)
    ch = cv2.waitKey()
    if save:
        if verbose: print 'Saving new image to %s/line_detection.jpg' % os.getcwd()
        cv2.imwrite('line_detection.jpg', img)

def main():
    parser = OptionParser(usage='%prog [options] path')
    parser.add_option('-i', dest='img')
    parser.add_option('-c', action='store_true', dest='connect')
    parser.add_option('-s', action='store_true', dest='save')
    parser.add_option('-v', action='store_true', dest='verbose')
    parser.add_option('-p', action='store_true', dest='plane')
    options, args = parser.parse_args()  

    if options.img:
        img = cv2.imread(options.img)
        if img is None:
            raise ValueError('Invalid image file location "%s".' % options.img)
        else:
            draw_lines(img, options.connect, options.save, options.verbose, options.plane)
    else:
        usage()
        sys.exit()

if __name__ == "__main__":
    main()
