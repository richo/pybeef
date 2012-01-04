#!/usr/bin/env python
# richo <richo@psych0tik.net>
# '10 '11
# This code is released into the public domain
# Under the terms of the WTFPL or GPLv2 at your option

# Credit/links/patches are appreciated though

import os
import sys

try:
    # Hack to make this load properly on a mod_python webserver
    from webapp_handle import serve_self
    # I don't get why index = serve_self doesn't work..
    def index(req):
        return serve_self(req)
except ImportError:
    pass


# TODO
# - Make the parser more intuitive.
#  The functions to actually construct the stack are probably neccesary, but
#  I think we can safely do some test on the stack to see what the last thing
#  was, and either add to it or the stack (recursively)
# - Have a crack at making it faster, and remove code dupes in __call__()
# - Documentation?

def usage():
    pass
class bf(object):
    """a brainfuck interpreter.
    Create your object, push a bunch of instructions (or hell, a whole source file)
    to it with .push(instruction)
    then call the object to evaluate
    """
    def __init__(self):
        self.pointer = 0
        self.buf = [0]
        self.stack = []
        self.ref_stack = []
        self.current_loop = self.stack
        self.cmds = {
                "<": lambda: self.current_loop.append(self.sh_left),
                ">": lambda: self.current_loop.append(self.sh_right),
                "+": lambda: self.current_loop.append(self.po_add),
                "-": lambda: self.current_loop.append(self.po_sub),
                ".": lambda: self.current_loop.append(self.po_out),
                ",": lambda: self.current_loop.append(self.po_in),
                "[": self.a_lo_enter,
                "]": self.a_lo_exit
            }
    def __call__(self):
        # This is basically the same logic, with a slight tweak
        self.exec_stack(self.stack, topLevel=True)
    def exec_stack(self, stack, topLevel=False):
        while self.buf[self.pointer] != 0 or topLevel:
            for i in stack:
                if type(i) == list:
                    self.exec_stack(i)
                else:
                    i()
            if topLevel:
                break

    def push(self, inst):
        """Push a bf instruction onto the stack"""
        if inst in self.cmds:
            self.cmds[inst]()

# These are the methods which handle the physical structure of the stack
# We guarantee that dumping code into self.current_loop will add it to the end
# of the current execution
    def a_lo_enter(self):
        self.ref_stack.append(self.current_loop)
        self.current_loop.append([])
        self.current_loop = self.current_loop[-1]
    def a_lo_exit(self):
        self.current_loop = self.ref_stack.pop(-1)
#
# Really I could probably lambda these but it'd be unreadable
#
    def sh_left(self):
        if self.pointer == 0:
            # This looks wrong at first, but remember that the pointer
            # is not absolute... ;)
            self.buf = [0] + self.buf
        else:
            self.pointer -= 1
    def sh_right(self):
        if self.pointer == len(self.buf)-1:
            self.buf.append(0)
        self.pointer += 1
# TODO: There is no official spec, but most suggest that these should wrap some point like a signed
# int in C
    def po_add(self):
        self.buf[self.pointer] += 1
    def po_sub(self):
        self.buf[self.pointer] -= 1
    def po_out(self):
        sys.stdout.write(chr(self.buf[self.pointer]))
    def po_in(self):
        # XXX I'm reasonably sure that this doesn't work.
        self.buf[self.pointer] = ord(sys.stdin.read(1))

def main(args):
    #cmds = '<>[]+-.,'
    obj = bf()
    fh = open(args[0], 'r')
    for line in fh:
        for char in line:
            obj.push(char)
    obj()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        exit()
    main(sys.argv[1:])
