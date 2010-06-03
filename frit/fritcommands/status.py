#!/usr/bin/python
"""
status command
"""

import fritutils.termout

def status(Evidences):
    """
    Print a status report for all evidences
    """
    fritutils.termout.printMessage("Frit Status:")
    for evi in Evidences:
        fritutils.termout.printMessage('\t%s : %s' % (evi.configName,evi.fileName))
        locklist = evi.lockList()
        if len(locklist) > 0:
            ll = ' '.join(locklist)
            fritutils.termout.printNormal('\t\tLocked by: %s' % ll)
        if len(evi.fileSystems) > 0:
            for fs in evi.fileSystems:
                fritutils.termout.printMessage('\t\t%s (format: %s , offset: %d)' % (fs.configName, fs.getFormat(),fs.offset))
