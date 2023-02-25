#!/usr/local/bin/python3.6

from os import statvfs

# Assumption!
# These are the mountpoints we care to check.
# We assume these exist
# We assume these file systems are necessary and sufficent

# Create a key-value pair of mountpoint : free space
# Assumption is 0 free space


def Disk_Free(mpfs):
    '''Expects a dictionary object
    Each key should be a mount point of the file system.
    '''
    for mp in mpfs:
        sfs = statvfs(mp)
        mpfs[mp] = (sfs.f_bavail / sfs.f_blocks) * 100

    return mpfs

if __name__ == '__main__':
    mp = ['/u01', '/u02', '/u03', '/u03/backup', '/redo01', '/redo02']
    mpfs = { m : 0 for m in mp}
    Disk_Free(mpfs)
