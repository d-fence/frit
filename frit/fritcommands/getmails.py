#!/usr/bin/python
"""
getmails command.
This command is used to used to extract emails from mailboxes.
Currently, it supports Oulook PST,OST and Outlook express DBX files.
"""

import os
import fritutils.termout
import fritutils.fritobjects
import fritutils.fritdb as fritModel
import fritutils.fritemails

def factory(Evidences,args):
    for evi in Evidences:
        for fs in evi.fileSystems:
            # Searching for PST and OST files first
            # Working on normal files first
            for filepath in fs.ExtensionsOriginalFiles(u'.pst'):
                exportPath = os.path.join('.frit/extractions/emails/outlook/', filepath)
                pstPath = os.path.join(fs.fsMountPoint, filepath)
                if os.path.isdir(exportPath + '.export'):
                    fritutils.termout.printWarning('Extraction path already exists. Not exporting.')
                else:
                    fs.mount('getmails', 'Extracting Outlook emails')
                    fritutils.fritemails.pffExport(pstPath,exportPath)
                    fs.umount('getmails')
            
            # Working on undeleted filesize
            # It's probably quicker to walk undelete files than to query db
            for filepath in fs.listUndeleted():
                if os.path.splitext(filepath)[1] == u'.pst':
                    print filepath
    
