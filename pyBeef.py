#!/usr/bin/env python
# richo <richo@psych0tik.net>
# '10 '11
# This code is released into the public domain
# Under the terms of the WTFPL or GPLv2 at your option

# Credit/links/patches are appreciated though

import os
import sys

# TODO
# - Make the parser more intuitive.
#  The functions to actually construct the stack are probably neccesary, but
#  I think we can safely do some test on the stack to see what the last thing
#  was, and either add to it or the stack (recursively)
# - Have a crack at making it faster, and remove code dupes in __call__()
# - Documentation?

def usage():
    print("usage: %s file.bf" % sys.argv[0])
    exit()
class BF(object):
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
    def run(self):
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

    def a_lo_enter(self):
        self.ref_stack.append(self.current_loop)
        self.current_loop.append([])
        self.current_loop = self.current_loop[-1]
    def a_lo_exit(self):
        self.current_loop = self.ref_stack.pop(-1)
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
#   This should really implement a custom data structure like a doubly linked
#   list so that it wraps after
    def po_add(self):
        self.buf[self.pointer] += 1
    def po_sub(self):
        self.buf[self.pointer] -= 1
    def po_out(self):
        sys.stdout.write(chr(self.buf[self.pointer]))
    def po_in(self):
        # Pray noone gives us unicode
        self.buf[self.pointer] = ord(sys.stdin.read(1))

def main(source):
    obj = BF()
    try:
        fh = open(source, 'r')
    except IOError as e:
        print(e)
        exit()
    for line in fh:
        for char in line:
            obj.push(char)
    obj.run()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    main(sys.argv[1])
