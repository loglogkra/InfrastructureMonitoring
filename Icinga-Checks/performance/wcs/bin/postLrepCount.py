#!/usr/local/bin/python3.6

import sys
import argparse
import sysperf.query_lrepCount as Query
import sysperf.post_procCheckResult as Post


"""
Description:
    Posts lrep count from previous hour to Icinga master node API.
Expected use: 
  Called from Cron job > crontarget_lrepCount.sh > __main__ (args)
  Calls query_lrepCount.py to query lrep information
  Calls post_procCheckResult.py to POST lrep information
Expected argument input: 
    $python3 postLrepCount.py --date 04-Dec-2019-10 --orastring "LBND07_TS_TRACKING;LBND07_TS_TRACKING;SWDB-ORACLE00"
Expected return value (good case): 
    (option 1) Unformatted: float of lrep count, e.g. 1.00000
    (option 2) Formatted: tag;42;0;0;1;Jan;0
Expected return value (bad case):     
    Print to stdout
    Fail silently
Goal:
    Return lrep count for the previous hour from which this script was called.
    Expected to be called by cron once each hour
Steps:    
    Call to query tracking db
    return value from query
    post value, formatted, to Icinga master node API  
    i.e.
    HERE > master node API > Notification Command > DB
"""


def Main(datestring, dbinfo):
    qresult = Query.DbGetLocationReports(datestring, dbinfo, apiFormatted=True)
    if qresult[0] == 'problem':
        for elem in qresult:
            print(elem)
        return

    palerts = Post.PostProcessCheckResult(qresult)
    if len(palerts) >= 1:
        for elem in palerts:
            print(elem)
        return



def GetArgs():
    parser = argparse.ArgumentParser(
             description='Process args for online backup log duration.')
    parser.add_argument('-d', '--date', required=True, action='store',
                       help='Current formatted date (DD-Mon-YYYY-Hr). e.g. 04-Dec-2019-10')
    parser.add_argument('-o', '--orastring', required=True, action='store',
                       help='Information for Oracle target, semi-colon delimeted. Specify target user-- do not use SYS unless it is a table specifically owned by SYS! e.g. DB_USER;DB_DBPASS;DB_INSTANCE_NAME')
    args = parser.parse_args()
    return args
    

if __name__ == '__main__':
    """ Sample call
        $python3 postLrepCount.py --date 04-Dec-2019-10 --orastring "LBND07_TS_TRACKING;LBND07_TS_TRACKING;SWDB-ORACLE00"
    """
    args = GetArgs() 
    Main(args.date, args.orastring)