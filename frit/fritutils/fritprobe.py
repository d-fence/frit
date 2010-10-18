#!/usr/bin/python
"""
A module to probe different file formats.
"""

import fritutils

def pffProbe(filePath):
    buf = fritutils.getBuffer(filePath,0,512)
    if buf[0:4] == '\x21\x42\x44\x4e':
        return True
    else:
        return False
