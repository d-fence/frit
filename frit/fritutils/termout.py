#!/usr/bin/python

"""
Various utilities for FRIT.
"""

import sys

COLORS = { 'red' : "\033[31m" , 'green' : "\033[32m", 'yellow' : "\033[33m" }

def hasColor():
    """
    Verify if the terminal support colors and return True or False.
    """
    if hasattr(sys.stdout, 'isatty'):
        if sys.stdout.isatty():
            return True
        else:
            return False

def smartprint(s,color):
    if hasColor():
        toPrint = "\033[95m" + COLORS[color] + s + "\033[0m"
        print >> sys.stderr, toPrint
    else:
        print >> sys.stderr, s

def printWarning(s):
    smartprint(s,'red')

def printSuccess(s):
    smartprint(s,'green')
    
def printMessage(s):
    smartprint(s,'yellow')
    
def printNormal(s):
    print s
