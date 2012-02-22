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
        self.stack_depth = 0
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
        """Commence execution
        """
        # TODO The implementation insinates that you should be able to push a
        # stack of insctructions, run them, add some more and then run them. If
        # you try that, you'll get both sets of instructions the second tme.
        self.exec_stack(self.stack)
    def exec_stack(self, stack):
        """Recursively executute a stack
        A stack is basically defined as a series of commands nested inside a
        set of loop operators, however the toplevel program is contained with a
        stack, and it's this constraint on not testing the value of the cell
        under the instruction pointer leaves us with the test for stack depth
        """
        while True:
            if self.buf[self.pointer] == 0 and self.stack_depth:
                break
            for i in stack:
                if type(i) == list:
                    self.stack_depth += 1
                    self.exec_stack(i)
                    self.stack_depth -= 1
                else:
                    i()
            if not self.stack_depth:
                break

    def push(self, inst):
        """Push a bf instruction onto the stack"""
        if inst in self.cmds:
            self.cmds[inst]()

    def a_lo_enter(self):
        """Loop Enter
        Creates a new stack, points current to it so that subsequent pushes
        enter the new context
        """
        self.ref_stack.append(self.current_loop)
        self.current_loop.append([])
        self.current_loop = self.current_loop[-1]
    def a_lo_exit(self):
        """Loop Exit
        Pop one level off the top of the execution stack, effectively unrolling
        one layer
        """
        self.current_loop = self.ref_stack.pop(-1)
    def sh_left(self):
        """Shift Left
        Shift the pointer one frame to the left, creating and initialising the
        target cell with a value of zero if necessary
        """
        if self.pointer == 0:
            # This looks wrong at first, but remember that the pointer
            # is not absolute... ;)
            self.buf = [0] + self.buf
        else:
            self.pointer -= 1
    def sh_right(self):
        """Shift Right
        Shift the pointer one frame to the right, creating and initialising the
        target cell with a value of zero if necessary
        """
        if self.pointer == len(self.buf)-1:
            self.buf.append(0)
        self.pointer += 1
#   TODO: This should really implement a custom data structure like a doubly
#   linked list so that it wraps after

#   TODO: Flag or environment variable that wraps the values at 256 or somesuch
    def po_add(self):
        """Increment
        Increment the cell pointed to by the instruction pointer by one
        """
        self.buf[self.pointer] += 1
    def po_sub(self):
        """Decrememnt
        Decrement the cell pointed to by the instruction pointer by one
        """
        self.buf[self.pointer] -= 1
    def po_out(self):
        """Output
        Convert the current cell to an ascii character and write to stdout
        """
        sys.stdout.write(chr(self.buf[self.pointer]))
    def po_in(self):
        """Input
        Retrieve a single byte from stdin, convert it to an integer, and store
        in the current cell
        """
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
