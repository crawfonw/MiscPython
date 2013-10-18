import cv
import cv2
import getopt
import sys

MODULE = cv2

def usage():
    print 'USAGE: python cvhelp.py -l [string]'

def lookup(s):
    funcs = dir(MODULE)
    for f in funcs:
        if s in f.lower():
            print f

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:m:', ['help', 'lookup', 'module'])
    except getopt.GetoptError, err:
        print 'Please type -h or --help for usage.'
        sys.exit(2)
    output = None
    verbose = False
    if not opts:
        usage()
        sys.exit()
    for o, a in opts:
        if o in ('-l', '--lookup'):
            lookup(a.lower())
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

if __name__ == "__main__":
    main()
