import sys
import argparse
from syshealth import check_cpu
from syshealth import check_disk
from syshealth import check_memory
from syshealth import check_services

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


def Main(args):
    alertMessages = []

    # Check CPU utilization
    cpuval = check_cpu.Cpu_Usage(args.cpu)
    for c in cpuval:
        alertMessages.append(f'Processor usage is polling above alert threashold -  \'{c}%\'')

    # Check the free memory
    memval = check_memory.Mem_Free(args.memory)
    for m in memval:
        alertMessages.append(f'Memory usage is above alert threashold -  \'{m}%\'')

    # Check disk space
    diskvals = check_disk.Disk_Free(args.volumes)
    for diskkey in diskvals:
        alertMessages.append(f'Disk space usage on volume is above alert threashold - \'{diskkey}\'')

    # Check services are running
    service_result = check_services.IsService_Running(args.services)
    for s in service_result:
        alertMessages.append(f'Service is not running - \'{s}\'')

    # Report problems and close application
    if(len(alertMessages) > 0):
        for a in alertMessages:
            print(a)
        sys.exit(RETURN_CRITICAL)

    sys.exit(RETURN_OK)


def GetArgs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description='Arguments for checking the health of a given ESXI host.')
    parser.add_argument('-c', '--cpu', required=False, type=int, action='store',
                        help="Threashold value for what constitutes a hich cpu usage as a percent.")
    parser.add_argument('-m', '--memory', required=False, type=int, action='store',
                        help="Threashold value for remaining free memory as a percent.")
    parser.add_argument('-s', '--services', required=False, action='store',
                        help='Semicolon delimited list of services to check.')
    parser.add_argument('-v', '--volumes', required=False, action='store',
                        help="Semicolon delimited list of volumes and threasholds. e.g. 'C:\;10;D:\;5'")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    """$python check_health.py -c 95 -m 90 -s "MongoDB-NAUSATLVPMHE02;Tgw.Wcs.WarehouseServices.Server" -v "C:\\;10;D:\\;5"
    """
    args = GetArgs()

    Main(args)
