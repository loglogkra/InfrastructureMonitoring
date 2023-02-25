#!/usr/bin/python3.6
"""
Written by Michael Rice
Github: https://github.com/michaelrice
Website: https://michaelrice.github.io/
Blog: http://www.errr-online.com/
This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0
"""
from __future__ import print_function

import atexit

from pyVim.connect import SmartConnect, Disconnect

import alarm
import tools
import ssl
import argparse
import getpass


def ListHostAlarms(args):
    context = None
    
    if args.disable_ssl_verification:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE

    SI = SmartConnect(host=args.host,
                      user=args.user,
                      pwd=args.password,
                      port=args.port,
                      sslContext=context)

    atexit.register(Disconnect, SI)
    
    INDEX = SI.content.searchIndex
        
    #content = SI.RetrieveContent()
    #search_index = content.searchIndex
        
    if INDEX:
        #HOST = INDEX.FindByUuid(datacenter=None, uuid=args.uuid, vmSearch=False)
        HOST = INDEX.FindByDnsName(dnsName=args.vihost, vmSearch=False)
        alarm.print_triggered_alarms(entity=HOST)
        # Since the above method will list all of the triggered alarms we will now
        # prompt the user for the entity info needed to reset an alarm from red
        # to green
        try:
            alarm_mor = input("Enter the alarm_moref from above to reset the "
                                  "alarm to green: ")
        except KeyboardInterrupt:
            # this is useful in case the user decides to quit and hits control-c
            print()
            raise SystemExit
        if alarm_mor:
            if alarm.reset_alarm(entity_moref=HOST._moId,
                                 entity_type='HostSystem',
                                 alarm_moref=alarm_mor.strip(),
                                 service_instance=SI):
                print("Successfully reset alarm {0} to green.".format(alarm_mor))
    else:
        print("Unable to create a SearchIndex.")
        
        
def GetArgs():
    parser = argparse.ArgumentParser(
             description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=True, action='store',
                       help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                       help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                       help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                       help='Password to use when connecting to host')
    '''
    parser.add_argument("-x", "--uuid", required=True, action="store",
                       help="The UUID of the HostSystem to list triggered alarms for.")
    '''
    parser.add_argument('-x', '--vihost',
                        required=True,
                        action='store',
                        help='Name of ESXi host as seen in vCenter Server')
                        
    parser.add_argument('-S', '--disable_ssl_verification',
                        required=False, action='store_true',
                        help='Disable ssl host certificate verification')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = GetArgs()
    
    if not args.password:
        args.password = getpass.getpass(prompt='Enter password for host %s and '
                                          'user %s: ' % (args.host,args.user))

    ListHostAlarms(args)
