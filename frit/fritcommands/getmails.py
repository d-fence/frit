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
import fritutils.fritlog

logger = fritutils.fritlog.loggers['getmailsLog']

def getExportPath(filepath,fs):
    exportPath = os.path.join('.frit/extractions/emails/outlook/', fs.evidenceConfigName, fs.configName, filepath)
    return exportPath

def getOutlookMailsFromWalk(fs,extension):
    logger.info('Starting to search for "%s" files from walk' % extension)
    fs.mount('getmails', 'Walking for Outlook emails')
    for filepath in fs.listFiles():
        ext = os.path.splitext(filepath)[1]
        if ext == extension:
            logger.info('File "%s" found, starting extraction' % filepath)
            filepath = filepath.replace(fs.fsMountPoint,'')
            if filepath[0] == '/':
                filepath = filepath[1:]
            exportPath = getExportPath(filepath,fs)
            pathToCreate = os.path.split(exportPath)[0]
            pstPath = os.path.join(fs.fsMountPoint, filepath)
            if os.path.isdir(exportPath + '.export'):
                fritutils.termout.printWarning('Extraction path "%s" already exists. Not exporting.' % (exportPath + '.export'))
            else:
                if fritutils.fritprobe.pffProbe(pstPath):
                    if not os.path.isdir(pathToCreate):
                        os.makedirs(pathToCreate)
                    fritutils.fritemails.pffExport(pstPath,exportPath)
                else:
                    fritutils.termout.printWarning('%s is not a PFF file.' % pstPath)
    fs.umount('getmails')
    fs.evidence.umount('getmails')

def getOutlookMailsFromDb(fs,extension):
    logger.info('Starting to search for "%s" files from database' % extension)
    for filepath in fs.ExtensionsOriginalFiles(extension,u'Normal'):
        logger.info('File "%s" found' % filepath)
        exportPath = getExportPath(filepath,fs)
        pathToCreate = os.path.split(exportPath)[0]
        pstPath = os.path.join(fs.fsMountPoint, filepath)
        if os.path.isdir(exportPath + '.export'):
            fritutils.termout.printWarning('Extraction path "%s" already exists. Not exporting.' % (exportPath + '.export'))
            logger.info('Extraction path "%s" already exists. Not exporting.' % (exportPath + '.export'))
        else:
            fs.mount('getmails', 'Extracting Outlook emails')
            if fritutils.fritprobe.pffProbe(pstPath):
                if not os.path.isdir(pathToCreate):
                    os.makedirs(pathToCreate)
                fritutils.fritemails.pffExport(pstPath,exportPath)
            else:
                fritutils.termout.printWarning('%s is not a PFF file.' % pstPath)
            fs.umount('getmails')

def getOutlookUndeletedFromDb(fs):
    for filepath in fs.listUndeleted():
        if os.path.splitext(filepath)[1] == u'.pst' or os.path.splitext(filepath)[1] == u'.ost' :
            cleanedPath = filepath.replace('.frit/extractions/','')
            exportPath = getExportPath(cleanedPath,fs)
            pathToCreate = os.path.split(exportPath)[0]
            if os.path.isdir(exportPath + '.export'):
                fritutils.termout.printWarning('Extraction path "%s" already exists. Not exporting.' % (exportPath + '.export'))
            else:
                if fritutils.fritprobe.pffProbe(filepath):
                    if not os.path.isdir(pathToCreate):
                        os.makedirs(pathToCreate)
                    fritutils.fritemails.pffExport(filepath,exportPath)
            
def factory(Evidences,args):
    logger.info('Starting getmails command')
    if args and '--walk' in args:
        logger.info('Using "--walk" argument.')
        for evi in Evidences:
            logger.info('Working on evidence "%s"' % evi.configName)
            for fs in evi.fileSystems:
                logger.info('Working on filesystem "%s"' % fs.configName)
                getOutlookMailsFromWalk(fs,u'.pst')
                getOutlookMailsFromWalk(fs,u'.ost')
    else:
        logger.info('Searching mails from database.')
        if fritModel.dbExists():
            for evi in Evidences:
                for fs in evi.fileSystems:
                    # Searching for PST and OST files first
                    # Working on normal files first
                    getOutlookMailsFromDb(fs,u'.pst')
                    getOutlookMailsFromDb(fs,u'.ost')
        else:
            fritutils.termout.printWarning('You need to create the database first with the "store create" command or use the "--walk" option')
            
    # Working on undeleted files
    # It's probably quicker to walk undelete files than to query db
    for evi in Evidences:
        for fs in evi.fileSystems:
            getOutlookUndeletedFromDb(fs)
