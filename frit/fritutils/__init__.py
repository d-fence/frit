#!/usr/bin/python

import os
import os.path
import sys
import re
import fritutils.termout

def getCommand(args):
    command = args[0]
    if len(args) > 1:
        commandArgs = args[1:]
    else:
        commandArgs= None
    return (command,commandArgs)

def noBadPath():
    """
    A function to check if the CWD is an allowed path to use it as a frit repository.
    """
    bad = False
    cwd = os.getcwd()
    badPathes = ('/','/home')
    badTrees = ('^/usr','^/var','^/etc','^/lib.*','^/boot','^/bin','^/sbin','^/proc','^/sys')
    for bt in badTrees:
        btr = re.compile(bt)
        if btr.search(cwd):
            bad = True

    if cwd in badPathes:
        bad = True

    if bad :
        fritutils.termout.printWarning("You cannot use frit from the '%s' directory" % cwd)
        sys.exit(1)

def isCwdFrit():
    """
    A function to check if there is already a .frit directory in CWD
    """
    cwd = os.getcwd()
    fritDir = os.path.join(cwd,'.frit')
    if os.path.exists(fritDir):
        return True
    else:
        return False

def humanize(x):
    """
    Function to convert a number of bytes in something more human readable
    """
    if x:
        units = { 'KiB': 1024, 'MiB': 1024*1024, 'GiB': 1024*1024*1024, 'TiB': 1024*1024*1024*1024 }
        r = "%d bytes" % x
        for u,v in units.items():
            if x < v:
                break
            r = "%d %s" % (x/v,u)
        return r
    else:
        return 0

def getOffset(offString):
    """
    A function to get the offset from the config "offset" string.
    It must return an integer representing the offset in bytes.
    offString can be a single number of bytes or a calculation
    """
    evalRe = re.compile('\+|\*|\-|\/')
    numRe = re.compile('^\d+$')
    if evalRe.search(offString):
        return eval(offString)
    elif numRe.search(offString):
        return int(offString)
    else:
        fritutils.termout.printWarning("Bad offset option !")
        sys.exit(1)

def unicodify(x):
    try:
        y = unicode(x.decode('utf-8'))
    except:
        print >> sys.stderr, "ERROR TRANSCODING %s TO UNICODE" % x
        y = x
    return y
