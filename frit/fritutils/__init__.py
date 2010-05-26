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
    cwd = os.getcwd()
    fritDir = os.path.join(cwd,'.frit')
    if os.path.exists(fritDir):
        return True
    else:
        return False
