# Forensic Robust Investigation Toolkit

## Introduction

The idea behind frit was inspired by the use of git.
It's a command line tool to ease the use of already avaliable
open source forensic tools.
It will help in file triage and dealing with multiple forensic
aquired images.

For example, it will mount and unmount filesystems when needed.
You can even launch different tasks at the same time in different consoles.
Frit will take care of locking mounted filesystems to avoid that another
instance unmount the filesystems accidentally.

Frit is written in Python.

## Dependencies

FRIT is still using python 2.7

Debian package name is between parentheses.

* elixir (python-elixir)
* sqlaclhemy (python-sqlalchemy)
* configobj (python-configobj)
* fuse iso (fuse-iso)
* libpff (pff-tools)
* ssdeep (ssdeep)
* afflib (afflib-tools)
* fuse-utils (fuse-utils)
* ntfs-3g (ntfs-3g)
* losetup, mount, umount (mount)
* sudo (sudo)
* fuseext2 (fuseext2)
* rofs (rofs)
* ntfsundelete (ntfsprogs)
* python-pyssdeep (No debian package yet - http://code.google.com/p/pyssdeep/)
* ewf tools (ewf-tools)
* pyvshadow + vshadowmount (https://github.com/libyal/libvshadow)

## Installation

to be written

## prerequisite

The following prerequisite and advises have to be carrefully read.
You must understand what you do because they could be a security risk
in untrusted environement.
They are to be used when you are the only user of the machine or when
you absolutely trust all the users of the frit program AND the users of
the machine where it's installed.

### Loop devices

Make sure there are enough free loop devices on the system, for example,
modify /etc/modules and insert this line:
loop max_loop=64
This will make 64 loop devices available.

### Block devices

Make sure that the user can use the block devices.
On Debian it have to belong to the 'disk' group.

### NTFS-3G

Make sure that your user can use ntfs-3g, for example:

- add an ntfsuser group
- make your user belonging to this group
- change the group of the ntfs-3g binary:

  sudo chown root.ntfsuser $(which ntfs-3g)

- make the ntfs-3g binary suid root and only executable by the group:

  sudo chmod 4750 $(which ntfs-3g)

### sudo

Frit sometimes needs root privileges, for example when it need to mount a
filesystem like FAT.
For this, it uses the "sudo" command. Sudo will ask for password when needed
but most of the time, the user will not be in front of the console when it
happens.
That's why you may want to allow your user to gain root privileges when using
frit without the need of a password.
Be aware of the security risk.

### fuse

You should enable the option "user_allow_other" in /etc/fuse.conf

## Usage

Frit is a command line tool. The synospis is:

    frit COMMAND ARGS [EvidenceX/File Name] [EvidenceY/File Name] ...

### Init

First of all, forensic evidences have to be placed in a same directory tree.
At the root of this tree :

    $ frit init

The init command will create the hidden diretory .frit and will create a
basic configuration file .frit/config.

This config file have to be edited and modified in order to have:
A section by evidence file and a subsection by filesystem found on this
evidence.

    For example:
    [Evidence1]
        Name=pc-badguy.aff
        Format=aff
        [[Filesystem1]]
            Format=NTFS
            Offset=63*512
    [Evidence2]
        Name=pc-badguy2.aff
        Format=aff
        [[Filesystem1]]
            Format=NTFS
            Offset=32256
        [[Filesystem2]]
            Format=FAT
            Offset=71328600*512

The "Name" parameter is the filepath to the evidence.
The "Format" parameter in the evidence section is the format used by the
forensic image (frit currently supported raw files (dd), aff (advenced forensic
format and ewf (encase)).

The "Filesystem#number" subsection must contain the format of this filesystem
(frit currently support NTFS, FAT, HFSPLUS, EXT2/3, ISO9660, ROFS) 
and the offset in bytes where to find this filesystem on the image.

#### Rofs special case.

Instead of using a container file (a forensic image copy), one can use a simple
directory instead. For example, in case of a forensic copy was not possible,
an investigator simply copy a directory structure.
This is where ROFS comes in. Frit can do a mirror mount of this directory but
in Read Only mount thanks to the ROFS fuse file system.
Offset MUST be set to 0. The directory cannot be outside of the frit working
directory (you cannot set it to ../../other_dir).

Configuration example:

    [Evidence1]
        Name=server-files-directory
        Format=rofs
        [[Filesystem1]]
            Format=ROFS
            Offset=0

### add

The "add" command is used to add an evidence to the config file, without
manually edit this config file.

The arguments to the "add" command are file names of the evidences that
you want to add.

Frit will try to identify wich kind of container it is.
Then it will mount the container and try to probe for the filesystems
that are present in this container.

At this moment, Frit is able to recognize thos containers:

- raw DD
- AFF
- EWF

The filesystems recognized are:

- NTFS
- FAT

The partitioning schemes recognized are:

- MSDOS partition types
- No partitioning at all

### mount

The "mount" command will mount each filesystem from each evidence.
It's useful to test that your configuration file is working.
The filesystems are mounted in
".frit/filesystems/Evidence#number/Filesystem#number".

You can then use them normally.

If you are only intersted in mounting containers to access a raw image,
for example to use a carving tool on the raw image, you can use the "mount
containers" command.

### store

Frit use a sqlite3 database to store various elements about the files.
The database itself is a simple slite file stored in ".frit/frit.sqlite".

The metadata that will be stored in the database are:
files names, files pathes, avalaible files dates, files mime types, files
extensions,
md5, sha1 and ssdeep hashes ... and more to come.

The first step is to create the initial database with the command:

    $ frit store create

This will mount the filesystems if needed and will store basic informations
about files: pathes, names, dates and extensions.

If you decide to add a new evidence in your case, you will have to updae the
database.
Use the "store update" command for this purpose.
Once you added the new evidence in your config file, use:

    $ frit store update

### extensions

The extension command is used to manipulate files based on their extensions.
This command has to be used after the "store init" command is finished.

By default, the "extensions" command works on all files states (Normal,
Undeleted, Contained, Carved)

If you want to work only on certain files states, you can provide one or more
of these options:

    --normal
    --undeleted
    --contained
    --carved

#### Counting extensions

    $ frit extensions count

This command will list all extensions found on the filesystems along with their
numbers and the total size used by them.

If you pass an extension list as parameter, it will show the count for those
extensions only.
For example, if you want to count "xls" and "doc" files, use this command:

    $ frit extensions count .xls .doc

#### List files matching an extension criteria

If you want to list all files with an "xls" extension, you can try this command:

    $ frit extensions list .xls

It will list the full pathname (including the "./frit/..." part) of the ".xls"
files. You can use more than one criteria. If you omit an extension criteria, it
will list all files, sorted by their extension.

#### Extract files based on their extensions

Let's imagine that we want to extract all "pdf" and "xls" from all evidences.
You can use this command:

    $ frit extensions extract .pdf .xls

This will extract the corresponding files in the directory
".frit/extractions/by_extensions/Evidence#number/filesystem#number/extension/..."
The fullpath will be reconstructed behind this path.

If you don't want to have a directory by extension, use the merge option like
this:

    $ frit extensions extract --merge .pdf .xls .doc

You can also provide extensions list into the config file.
For exemple:

    [Extensions]
        Office = .odt .ods .odp .doc .docx .xls .ppt .pptx .pdf
        Images = .jpg .jpeg .png .tif
        Perso = .dwf .dbx

This entry in ".frit/config" file will give you 3 lists of extensions.
So, if you use this command:

    $ frit extensions extract Office Images .txt

Will extract "odt .ods .odp .doc .docx .xls .ppt .pptx .pdf .jpg .jpeg .png
 .tif .txt"

### hashes

This command is used to manipulate file hashes in frit environment.
This command need arguments.
To manipulate hashes, you first need to have a initial database, so you need
to use the store command first.

    $ frit store create

#### Update the database

The update command will calculates md5, sha1, sha256 and ssdeep hashes for all
files and update the database.

    $ frit hashes update

#### Searching for hashes

You can search for md5 like this:
$ frit hashes md5search a743b

This command will search for a md5 hash begining by "a743b".
A hash to search have at least to be 3 characters long.
sha1 and sha256 can be searched with sha1search and sha256search

#### Searching for ssdeep hashes

An investigator can search for a fragment of file using this method.
For example, an investigator find an MS Word document during the investigation
and he wants to know if similar docs are elsewhere on the other forensic images
copies.

First thing to do is to use ssdeep against this document to create a piecewise
hash like this:

    $ ssdeep README
    ssdeep,1.0--blocksize:hash:hash,filename
    48:aIylX3pU+GR+YGul0qWEnF80IzUbuHL946kEQIH8OtosKgIVi/X18fb:aHlnpU/vZWEnF809be94
    6kEjH5c6gb,"/usr/share/doc/python-pefile/README"

You can then search on all files stored in the frit database for a similar
file matching a score (on a scale of 100).

Example:

    $ frit ssdsearch 48:aIylX3pU+GR+YGul0qWEnF80IzUbuHL946kEQIH8OtosKgIVi/X18fb:aHl
    npU/vZWEnF809be946kEjH5c6gb 50

Will search for files matching this ssdeep hash on a score of 50.

#### csv dump of database

You can dump the all database with this command:

    $ frit hashes csvdump

It will dump the db like this:
Evidence name, File system name ,file name , md5 hash, sha1 hash, sha256 hash, 
ssdeep hash, file state

### undelete

Perform an undelete on filesystems and store the results in
'.frit/extractions/undeleted'.

Currently only ntfs is supported.

If the '--list' option is used, frit will list already undeleted files.

### getmails

Search for PST and OST outlook mailboxes files and extract their mails and
attachments using libpff.

The search is performed against the database, so the database have to be
created first.
If you want to search for those files by walking through the directories, you
must append the '--walk' option.

### status

The status command give a status of the frit system.
It parses the config file and describe the systems.
It shows if a container or a filesystem is locked by another instance of frit.
It also shows if a container or a filesystem is mounted.

#### status clean

In case of a crash or for another reason, the frit environement can be left in 
an inconsistent state.
For example:

- A file system is mounted but not locked
- A file system is locked but not mounted
- A file system is locked but the process which locked it is not running anymore
- ...

Those inconsistencies are shown in red. If the user want to clean it, he can
launch this command:

    $ frit status clean

It's possible that a clean command result in another inconsistency. In this case
the user have to launch this command until the system is completely clean.

#### database status

It's possible to have information about the frit sqlite database by issuing this
command:

    $ frit status database

### Unallocated sectors

It's sometimes useful to work on unallocated sectors of a disk image.
The "sectors" command may be used for exploring unallocated sectors.
The "mmls" sleuthkit tool is used by frit to search for unallocated sectors.
Some containers used by frit does not support unallocated sectors, like "rofs",
in those cases, the sectors command will have no effects.

#### sectors list

The "list" sub-command can be used to display a list of unallocated sectors:

    $ frit sectors list

#### sectors export

The "export" subcommand will export unallocated sectors in this directory:
".frit/extractions/sectors/EvidenceX/sectors_Y-Z/sectors_y-Z.dd", where X 
is the Evidence number, Y the starting sector and Z the ending sector number.

The consecutive sectors are exported in a single raw file.
If the "--split" option is used, the sectors are splitted using a file for each
exported sector.

## Specify an evidence

You can specify on which Evidence(s) you want to work on the command line.
For example, if you want to mount only the "Evidence3" and their filesystems,
you can use this command:

    $ frit mount Evidence3

You could also specify multiple ones. For example, this command will count
.xls .doc and .jpg extensions for Evidence3 and Evidence 5:

    $ frit extensions count .xls .doc .jpg Evidence3 Evidence5

It's also possible to specify an Evidence by its file name like this:

    $ frit store update my_nice_container.ewf

## Logs

frit uses a logging system. log files are stored in the ".frit/logs" directory.
There is one log file per frit process. It means that each time you launch a 
frit command, there is a new log files. This can quickly makes a lot of files.
File naming is like this :
frit-10046.log 
where the number is the PID of the frit process.

One can launch the "logs show" command to display the content of the log files.
Be aware that even the "logs show" command create a log entry that will be 
displayed too.

## Future

What is palnned in the future releases:

- carving
- file indexing
- ...

