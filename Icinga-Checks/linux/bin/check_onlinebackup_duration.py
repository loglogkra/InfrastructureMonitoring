#!/usr/local/bin/python3.6

import sys
import argparse
import re


"""
Utilize the syshealth package and report on the health of the system.
All checks that are necessary to determine the health of the system
should be called from this script and included in the syshealth package.

Expected use: This script is called by Icinga after install of syshealth pkg.
Expected argument input: 
    -l := location of onlinebackup.out
    -w := warning threashold in seconds
Expected return value (good case): sys.exit(0)
    This tells Icinga 'OK'
Expected return value (bad case): sys.exit(1) and stdout message
    sys.exit(1) tells Icinga 'Warning'.
    This check is a performance check and should only return OK or WARN.
    Performance checks always output performance value(s).
    Output to stdout is automatically returned to the master node.
    
Goal:
    Determine how long it took the most recent execution of the onlinebackup script to complete.

Steps:
    Parse the current onlinebackup.out file.
    Match on last line starting 'starting ONLINEBACKUP'
    Match on last line starting 'ONLINEBACKUP completed'
    Derive the datetime values from each matched line and find the difference in minutes.
    
Return:
    Value in minutes to stdout
    0/OK if value in minutes is < warning threashold
    1/WARN if value in minutes is >= warning threashold
"""

RETURN_OK = 0
RETURN_WARN = 1


def GetTimeDelta(start_stop_list):
    ''' Input expected to be list of time.
        time format expected to look like this:
            Fri, 08.11.2019 02:19:31
    '''  
    if len(start_stop_list) <= 1:
        print('No data could be read from the onlinebackup.sh output file. This is commonly due to log rollover and will be resolved by the next day check.')
        sys.exit(RETURN_WARN)
    
    start = re.split(', |\.|:| ', start_stop_list[0])
    stop = re.split(', |\.|:| ', start_stop_list[1])

    del_hour = int(stop[4]) - int(start[4])
    del_min = int(stop[5]) - int(start[5])
    
    timeDeltaMinutes = (del_hour * 60) + (del_min)
    
    return timeDeltaMinutes


def GetListStartStop(location):
    ''' Return the last (most recent) onlinebackup time strings.
        Strings are formatted like this:
            Fri, 08.11.2019 02:19:31
    '''
    retval = []
    with open(location, "r") as logfile:
        for line in logfile:
            if "ONLINEBACKUP" in line:
                retval.append(line[45:69])

    return retval[-2:]


def GetOnlineBackupDuration(args):
    start_stop_list = GetListStartStop(args.location)
    timeDeltaMinutes = GetTimeDelta(start_stop_list)

    print(timeDeltaMinutes)

    if timeDeltaMinutes >= args.warn:
        sys.exit(RETURN_WARN)

    sys.exit(RETURN_OK)
    

def GetArgs():
    parser = argparse.ArgumentParser(
             description='Process args for online backup log duration.')
    parser.add_argument('-l', '--location', required=True, action='store',
                       help='Full path of the onlinebackup log.')
    parser.add_argument('-w', '--warn', type=int, required=True, action='store',
                       help='Threashold in minutes to return a warning.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = GetArgs()  
    GetOnlineBackupDuration(args)