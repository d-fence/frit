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
import fritutils.fritprobe

def getOutlookMails(fs,extension):
    for filepath in fs.ExtensionsOriginalFiles(extension):
        exportPath = os.path.join('.frit/extractions/emails/outlook/', filepath)
        pathToCreate = os.path.join('.frit/extractions/emails/outlook/', os.path.split(filepath)[0])
        pstPath = os.path.join(fs.fsMountPoint, filepath)
        if os.path.isdir(exportPath + '.export'):
            fritutils.termout.printWarning('Extraction path "%s" already exists. Not exporting.' % (exportPath + '.export'))
        else:
            fs.mount('getmails', 'Extracting Outlook emails')
            if fritutils.fritprobe.pffProbe(pstPath):
                if not os.path.isdir(pathToCreate):
                    os.makedirs(pathToCreate)
                fritutils.fritemails.pffExport(pstPath,exportPath)
            else:
                fritutils.termout.printWarning('%s is not a PFF file.' % pstPath)
            fs.umount('getmails')

def getOutlookUndeleted(fs):
    for filepath in fs.listUndeleted():
        if os.path.splitext(filepath)[1] == u'.pst' or os.path.splitext(filepath)[1] == u'.ost' :
            cleanedPath = filepath.replace('.frit/extractions/','')
            exportPath = os.path.join('.frit/extractions/emails/outlook/' , cleanedPath)
            pathToCreate = os.path.join('.frit/extractions/emails/outlook/', os.path.split(cleanedPath)[0])
            if os.path.isdir(exportPath + '.export'):
                fritutils.termout.printWarning('Extraction path "%s" already exists. Not exporting.' % (exportPath + '.export'))
            else:
                if fritutils.fritprobe.pffProbe(filepath):
                    if not os.path.isdir(pathToCreate):
                        os.makedirs(pathToCreate)
                    fritutils.fritemails.pffExport(filepath,exportPath)
            
def factory(Evidences,args):
    for evi in Evidences:
        for fs in evi.fileSystems:
            # Searching for PST and OST files first
            # Working on normal files first
            getOutlookMails(fs,u'.pst')
            getOutlookMails(fs,u'.ost')
          
            # Working on undeleted files
            # It's probably quicker to walk undelete files than to query db
            getOutlookUndeleted(fs)
