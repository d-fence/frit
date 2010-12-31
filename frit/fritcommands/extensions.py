#!/usr/bin/python
"""
extensions command.
Used to manipulate file based on their extensions.
count is used to count extensions by filesystem.
list is used to list the filenames and path of the specified extensions.
extract is used to extract the specified extensions.
"""
import sys
import os.path
import shutil
import fritutils
import fritutils.termout
import fritutils.fritdb as fritModel
import fritutils.fritlog

logger = fritutils.fritlog.loggers['extensionsLog']

from sqlalchemy import select, func

def extractFile(toExtract,destination):
    extractBasename = os.path.basename(toExtract)
    if not os.path.exists(destination):
        os.makedirs(destination)
    if not os.path.exists(os.path.join(destination,extractBasename)):
        print 'Extracting "%s" to "%s"' % (toExtract,destination)
        try:
            shutil.copy2(toExtract,destination)
        except IOError:
            logger.error('Could not copy "%s" due to IO Error.' % toExtract)
            fritutils.termout.printWarning('Could not copy "%s" due to IO Error.' % toExtract)
    else:
        logger.debug('"%s" already exists' % os.path.join(destination+extractBasename))

def getExtLists(fritConf):
    # We have to convert to unicode from config file.
    toReturn = {}
    if fritConf.has_key('Extensions'):
        ed = fritConf['Extensions']
        for k in ed.keys():
            l = []
            for v in ed[k].split(' '):
                l.append(unicode(v))
            toReturn[k] = l
        return toReturn
    else:
        return {}

def factory(Evidences, args, options, fritConf):
    validArgs = ('count', 'extract','list')
    stateOptions = {'--normal':u'Normal','--contained':u'Contained','--undeleted':u'Undeleted','--carved':u'Carved'}
    definedExtensions = getExtLists(fritConf)
    states = []
    extList = []
    if not args or len(args) == 0:
        fritutils.termout.printWarning('extensions command need at least an argument to define an action (%s).' % ', '.join(validArgs))
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('extensions command need a valid argument (%s)' % ', '.join(validArgs))
        sys.exit(1)
    else:
        subcommand = args[0]
        args.remove(subcommand)        
        logger.info('subcommand issued: %s' % subcommand)
        if options:
            logger.info('options: %s' % ','.join(options))
            for o in options:
                if o in stateOptions.keys():
                    states.append(stateOptions[o])
        if len(states) == 0:        
            states = list(fritModel.FILESTATES)
        logger.info('states: %s' % ','.join(states))
        
        # Finding extensions to work with
        # Searching if one or more predefined extensions list is in the args
        for a in list(args):
            if a in definedExtensions.keys():
                logger.info('Extension list "%s" asked in command line.' % args)
                args.remove(a)
                extList.extend(definedExtensions[a])
        # the remaining args should be the extensions that we want to list
        # if there is no more args, we list all extensions
        if (not args or len(args) == 0) and len(extList) == 0:
            for ex in fritModel.elixir.session.query(fritModel.Extension.extension).all():
                extList.append(ex[0])
        else:
            for ex in args:
                extList.append(fritutils.unicodify(ex))        

        logger.info('Extensions: "%s"' % " ".join(extList))
            
        if subcommand == 'count':
            logger.info('Starting subcommand count')

            fritModel.listExtensions(Evidences,extList,states)
        elif subcommand == 'list':
            logger.info('Starting list subcommand.')
            for evi in Evidences:
                for fs in evi.fileSystems:
                    for ext in sorted(extList):
                        for state in states:
                            for fp in fs.ExtensionsFritFiles(ext,state):
                                fritutils.termout.printNormal(fp)
        elif subcommand == 'extract':
            logger.info('Starting extract subcommand')
            # The '--merge' option is used to merge extractions in a single
            # directory base instead of having a directory by extension.            
            merge = False
            if options and '--merge' in options:
                merge = True
            # we start by extracting 'normal files' because we need to mount the containers and filesystems
            if u'Normal' in states:
                logger.info('Starting Normal files extraction.')
                states.remove(u'Normal')
                for evi in Evidences:
                    # We count files to extract to see if it's needed to go further
                    enbe = evi.dbCountExtension(extList, u'Normal')
                    if enbe['count'] > 0:
                        logger.info('Found %d files to exctract, mounting Evidence container "%s".' % (enbe['count'],evi.configName))
                        evi.mount('extensions', 'Extracting files based on extensions')
                        for fs in evi.fileSystems:
                            fritutils.termout.printMessage("\t%s" % fs.evidence.configName + '/' + fs.configName)
                            fs.mount('extensions', 'Extracting files based on extensions')
                            for ext in sorted(extList):
                                nbe = fs.dbCountExtension(ext,u'Normal')
                                fritutils.termout.printMessage("Extracting %d files (%s)" % (nbe['count'],fritutils.humanize(nbe['size'])))
                                for filepath in fs.ExtensionsOriginalFiles(ext,u'Normal'):
                                    if ext == "No Extension":
                                        extPath = "no_extension"
                                    else:
                                        extPath = ext[1:]
                                    basePath = os.path.dirname(filepath)
                                    if merge:
                                        Destination = unicode(os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,basePath))
                                    else:
                                        Destination = unicode(os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,extPath,basePath))
                                    mountedPath = os.path.join(fs.fsMountPoint,filepath)
                                    extractFile(mountedPath,Destination)
                            fs.umount('extensions')
                        evi.umount('extensions')
                    else:
                        logger.info('No Normal files to extract on Evidence "%s", skipping' % evi.configName)
            for state in states:
                logger.info('Starting to extract %s files' % state)
                for evi in Evidences:
                    for fs in evi.fileSystems:
                        for ext in sorted(extList):
                            nbe = fs.dbCountExtension(ext,state)
                            if nbe['count'] >0 :
                                fritutils.termout.printMessage("Extracting %s %d files (%s)" % (state,nbe['count'],fritutils.humanize(nbe['size'])))
                                for filepath in fs.ExtensionsOriginalFiles(ext,state):
                                    # as we do not store the first character of the path, we have to re-add the '.'
                                    filepath = '.' + filepath
                                    if ext == "No Extension":
                                        extPath = "no_extension"
                                    else:
                                        extPath = ext[1:]
                                    # we dont want to have '.frit/extractions' in the middle of the destination path:
                                    basePath = os.path.dirname(filepath.replace('.frit/extractions/',''))
                                    if merge:
                                        Destination = unicode(os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,basePath))
                                    else:
                                        Destination = unicode(os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,extPath,basePath))
                                    extractFile(filepath,Destination)
                            else:
                                logger.info('Nothing found to extract on "%s".' % (evi.configName + '/' + fs.configName))
