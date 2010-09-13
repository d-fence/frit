#!/usr/bin/python
"""
Utilities to manipulate the frit configuration file.
"""
import re
import os
import fritutils.termout

def configContainersFiles(fritConfig):
    """
    A function that returns a list of filenames.
    """
    l = []
    EviRegex = re.compile("^Evidence\d+")
    for key in fritConfig:
        if EviRegex.search(key):
            l.append(os.path.abspath(fritConfig[key]['Name']))
    return l

def getNewEviName(fritConfig):
    num = 1
    while True:
        nkey = 'Evidence' + str(num)
        if nkey not in fritConfig.keys():
            return nkey
        num += 1

def addEvidence(fritConfig,Evidence):
    keyName = getNewEviName(fritConfig)
    fritConfig[keyName] = {}
    fritConfig[keyName]['Name'] = Evidence.fileName
    fritConfig[keyName]['Format'] = Evidence.getFormat()
    fritConfig.write()

