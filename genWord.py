#!/usr/bin/env python

# Generate brainfuck code to print all it's args
import os
import sys

def usage():
    pass

if len(sys.argv) == 1:
    usage()
    exit()
    
def owl(func):
    def __(string):
        func(string + "\n")
    return __

def main(args, base=10):
    if args == ["-"]:
        chars = sys.stdin.read()
    else:
        chars = " ".join(args).replace("\\n", "\n")+chr(10)
    outfile = open("genWord.bf", "w")
#   Hook a pretty writer to save space
    ow = owl(outfile.write)
    own = outfile.write
#   initialise our first char as a counter for iterating
    ow("+" * base)
#   While [0] > 0
    ow("[")
    lenbuf = ""
    for i in chars:
        #We're adding the 10's here
        own("    > %s" % ("+" * (ord(i) / base)))
#       Keep track of how many places back we need to go
        lenbuf += "<"
    own("    " + lenbuf)
    own("    -")
    ow("]")
# We're now done setting up the 10's
    for i in chars:
#   Increment the pointer, add the ones and print
        own("> %s ." % ("+" * (ord(i) % base)))


if __name__ == '__main__':
    main(sys.argv[1:])
