#!/usr/bin/env python3
import sys, getopt

if __name__ == "__main__":
    help = '''
    -i: 
    -h:
    '''
    print(sys.argv)
    if len(sys.argv) < 2:
        print(help)
        sys.exit(1)
    opts, args = getopt.getopt(sys.argv[1:], 'i:h:')
    print(opts)
    for opt, arg in opts:
        print(opt, arg)