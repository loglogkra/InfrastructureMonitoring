#!/usr/local/bin/python3.6

import sys
from syshealth import config
from syshealth import check_cpu
from syshealth import check_dbrecoveryfiledest
from syshealth import check_dbstatus
from syshealth import check_dbtablespace
from syshealth import check_disk
from syshealth import check_memory

"""
Utilize the syshealth package and report on the health of the system.
All checks that are necessary to determine the health of the system
should be called from this script and included in the syshealth package.

Expected use: This script is called by Icinga after install of syshealth pkg.
Expected argument input: None
Expected return value (good case): sys.exit(0)
    This tells Icinga 'OK'
Expected return value (bad case): sys.exit(2) and stdout message
    sys.exit(2) tells Icinga 'Critical'.
    All checks are health checks so any failure for any check should be crit.
    Discovered issue from a check is reported to stdout which will present
    to the Icinga master node.
"""

RETURN_OK = 0
RETURN_CRITICAL = 2


def main():
    alertMessages = []

    # Check CPU utilization
    cpuval = check_cpu.Cpu_Usage()
    if config.high_cpu_percent <= cpuval:
        alertMessages.append(f'CPU utilization \'{cpuval}%\'')

    # Check the free memory
    memval = check_memory.Mem_Free()
    if config.low_free_memory_percent >= memval:
        alertMessages.append(f'Remaining free memory \'{memval}%\'')

    # Check disk space
    diskvals = check_disk.Disk_Free(config.oracle_mount_points)
    for diskkey in diskvals:
        if config.low_free_disk_space >= diskvals[diskkey]:
            alertMessages.append(f'Remaining free disk space \'{diskkey}\' is \'{diskvals[diskkey]}%\'')

    dbstatusval = check_dbstatus.CheckDbStatus(config.db_check_positive)
    if config.db_check_positive != dbstatusval[0]:
        for val in dbstatusval:
            alertMessages.append(val)

    dbrecoveryfiledestval = check_dbrecoveryfiledest.CheckRecoveryFileDest(config.db_check_positive)
    if config.db_check_positive != dbrecoveryfiledestval[0]:
        for val in dbrecoveryfiledestval:
            alertMessages.append(val)

    dbtablespaceval = check_dbtablespace.CheckTsCapacity(config.db_check_positive)
    if config.db_check_positive != dbtablespaceval[0]:
        for val in dbtablespaceval:
            alertMessages.append(val)

    # Report problems and close application
    if(len(alertMessages) > 0):
        for a in alertMessages:
            print(a)
        sys.exit(RETURN_CRITICAL)

    sys.exit(RETURN_OK)


if __name__ == '__main__':
    main()
