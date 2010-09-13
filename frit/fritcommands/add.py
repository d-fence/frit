#!/usr/bin/python
"""
add command.
This command is used to add a file in a config file.
Frit then tries to recognize the container file and the contained file systems.
"""

import os
import fritutils.termout
import fritutils.containerprobe

def evidenceFileNames(Evidences):
    """
    A function that returns a list of filenames.
    """
    l = []
    for evi in Evidences:
        l.append(evi.FileName)
    return l

def factory(Evidences, args):
    """
    The factory receive the already defined Evidences and the remaining args.
    Those args are files that the user wants to add in the config file.
    We should first do some sanity checks to be sure that those files are
    readable ...
    """
    
    for fileName in args:
        fileName = os.path.abspath(fileName)
        if not os.path.exists(fileName):
            fritutils.termout.printWarning("File %s does't exist." % fileName)
        elif os.getcwd() not in fileName:
             fritutils.termout.printWarning("File %s is outside of the base directory." % fileName)
        elif fileName in evidenceFileNames(Evidences):
            fritutils.termout.printWarning("File %s already in config file." % fileName)
        else:
            cformat = fritutils.containerprobe.detectContainer(fileName)
            print cformat
