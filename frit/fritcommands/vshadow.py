#!/usr/bin/python
"""
vshadow
This command is made to work with MS Volume shadow copies.
The "list" subcommand will list all shadow copies found on NTFS FS
"""

import os
import fritutils
import fritutils.fritlog
import pyvshadow

logger = fritutils.fritlog.loggers['vshadowLog']

def vshadowList(Evidences, ags, options):
    for evi in Evidences:
        for fs in evi.fileSystems:
            fs.mount('vshadow','Used by vshadow command')
            if pyvshadow.check_volume_signature(fs.loopDevice):
                fritutils.termout.printSuccess("Volume shadow copy found on '{}/{}'".format(fs.evidenceConfigName,fs.configName))
                vshadowVol = pyvshadow.volume()
                vshadowVol.open(fs.loopDevice)
                fritutils.termout.printNormal("    Number of stores on volume: {}".format(vshadowVol.number_of_stores))
                for st in vshadowVol.get_stores():
                    fritutils.termout.printNormal("    Store identifier: {}".format(st.identifier))
                    fritutils.termout.printNormal("        Store creation time: {}".format(st.get_creation_time()))
                    fritutils.termout.printNormal("        Store size: {}".format(fritutils.humanize(st.size)))
                    fritutils.termout.printNormal("        Shadow-copy set ID: {}".format(st.copy_set_identifier))
                    fritutils.termout.printNormal("        Shadow-copy ID: {}".format(st.copy_identifier))
                vshadowVol.close()
            fs.umount('vshadow')
        if evi.isMounted():
            evi.umount('vshadow')
            


def factory(Evidences, args, options):
    if args and 'list' in args:
        vshadowList(Evidences, args, options)
