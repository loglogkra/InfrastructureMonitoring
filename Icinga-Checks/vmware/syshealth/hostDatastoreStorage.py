#!/usr/bin/python3.6
#
# Written by JM Lopez
# GitHub: https://github.com/jm66
# Email: jm@jmll.me
# Website: http://jose-manuel.me
#
# Note: Example code For testing purposes only
#
# This code has been released under the terms of the Apache-2.0 license
# http://opensource.org/licenses/Apache-2.0
#

import argparse
import atexit
import requests
import getpass
import ssl

#from tools import cli
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

# disable  urllib3 warnings
if hasattr(requests.packages.urllib3, 'disable_warnings'):
    requests.packages.urllib3.disable_warnings()


def get_obj(content, vim_type, name=None):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vim_type, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return [obj]
    else:
        return container.view


# http://stackoverflow.com/questions/1094841/
def sizeof_fmt(num):
    """
    Returns the human readable version of a file size

    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, item)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def print_datastore_info(ds_obj, diskThreashold):
    issueReport = []

    summary = ds_obj.summary
    ds_capacity = summary.capacity
    ds_freespace = summary.freeSpace
    ds_uncommitted = summary.uncommitted if summary.uncommitted else 0
    ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
    ds_overp = ds_provisioned - ds_capacity
    ds_overp_pct = (ds_overp * 100) / ds_capacity \
        if ds_capacity else 0

    # Freespace percentage check
    if (ds_freespace / ds_capacity) <= diskThreashold:
        issueReport.append("= LOW DISK SPACE =")
        issueReport.append( "Name                  : {}".format(summary.name))
        issueReport.append( "Capacity              : {}".format(sizeof_fmt(ds_capacity)))
        issueReport.append( "Free Space            : {}".format(sizeof_fmt(ds_freespace)))
        issueReport.append( "Uncommitted           : {}".format(sizeof_fmt(ds_uncommitted)))
        issueReport.append( "Provisioned           : {}".format(sizeof_fmt(ds_provisioned)))
        if ds_overp > 0:
            issueReport.append( "Over-provisioned      : {} / {}".format(
                sizeof_fmt(ds_overp),
                ds_overp_pct))
        issueReport.append( "Hosts                 : {}".format(len(ds_obj.host)))
        issueReport.append( "Virtual Machines      : {}".format(len(ds_obj.vm)))

    return issueReport


def ListDatastoreInfo(args, check_positive):
    ''' This is the method that is called by our icinga check
    '''
    retval = []
    
    password = args.password
    ''' Uncoment for debugging
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (args.host,args.user))
    '''
    if args.disable_ssl_verification:
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslContext.verify_mode = ssl.CERT_NONE

    # connect to vc
    si = SmartConnect(
        host=args.host,
        user=args.user,
        pwd=password,
        port=args.port,
        sslContext=sslContext)

    # disconnect vc
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    # Get list of ds mo
    ds_obj_list = get_obj(content, [vim.Datastore], args.name)

    # convert input to percentage
    diskThreashold = int(args.diskCrit) / 100

    for ds in ds_obj_list:
        result = print_datastore_info(ds, diskThreashold)
        for elem in result:
            retval.append(elem)

    if len(retval) > 0:
        return retval
    else:
        return [check_positive]

def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
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
   parser.add_argument('-n', '--name', required=False,
                       help="Name of the Datastore.")
   parser.add_argument('-d', '--diskCrit', default='100',
                       help="Freespace percentage that we alert on if we are below this value.")
   parser.add_argument('-S', '--disable_ssl_verification',
                       required=False,
                       action='store_true',
                       help='Disable ssl host certificate verification')
   args = parser.parse_args()
   return args


if __name__ == "__main__":
    # python.exe .\hostLocalStorage.py -s 10.14.12.36 -u tgw\baford -S
    args = GetArgs()
    ListDatastoreInfo(args)
