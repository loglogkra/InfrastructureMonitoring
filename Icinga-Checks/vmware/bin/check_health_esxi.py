#!/usr/bin/python3.6

import sys
import getpass
import argparse
from syshealth import getallvms
from syshealth import hostLocalStorage
from syshealth import hostDatastoreStorage

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

# Health checks get people out of bed in the middle of the night.
# They are either OK (ignore) or CRITICAL (call to action)
RETURN_OK = 0
RETURN_CRITICAL = 2
CHECK_POSITIVE = "OK" # if the check returns with this we have no problem.


def Main(args):
    alertMessages = []
    
    ''' Not needed unless debugging.
    '''
    if not args.password:
        args.password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))
    
    
    datastoreval = hostDatastoreStorage.ListDatastoreInfo(args, CHECK_POSITIVE)    
    if datastoreval[0] != CHECK_POSITIVE:
        for val in datastoreval:
            alertMessages.append(val)

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
    parser = argparse.ArgumentParser(
        description='Arguments for checking the health of a given ESXI host.')
    parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
    parser.add_argument('-n', '--name', required=False,
                       help="Name of the Datastore.")
    parser.add_argument('-S', '--disable_ssl_verification',
                       default=True, action='store_true',
                       help='Disable ssl host certificate verification')
    parser.add_argument('-j', '--json', default=False, action='store_true',
                       help='Output to JSON')    
    parser.add_argument('-d', '--diskCrit', default='100',
                       help="Freespace percentage that we alert on if we are below this value.")
                          
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    """python.exe .\check_health.py -s 10.136.250.72 -u root -S
    """
    args = GetArgs()
    Main(args)
