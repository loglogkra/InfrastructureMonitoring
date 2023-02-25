""" Collect the lrep count from a database.
    Expectations (This is used for...):
        Targeting a tracking database user (e.g. PROD_TS_TRACKING.TR_LREP)
        Collecting LREP record counts for the previous hour
        Cron job calls bash target script that will call this script
    Input:
        Current timestamp to determin the current hour and previous hour.
            ex. 04-Dec-2019-10
            Bash can provide this format: $date +'%d-%b-%Y-%H'
    Output:
        API call to master node
"""

import cx_Oracle
import argparse
import sys
import calendar


def DbGetLocationReports(datestring, dbinfo, apiFormatted=True):
    """ Orchestrate the query and processing of result
        Return either the structured result or list of alerts to the point of the call.
    """
    qresult = []
    alert = ['problem']
    month_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}

    date_elem_list = datestring.split('-')
    db_elem_list = dbinfo.split(';')

    if len(date_elem_list) != 4:
        alert.append("Bad input string. Incorrect number of datetime components. See usage (--help). \nOriginal string:" + datestring)
        return alert

    if len(db_elem_list) != 3:
        alert.append("Bad input string. Incorrect number of database parameters. See usage (--help). \nOriginal string: " + dbinfo)
        return alert

    day = date_elem_list[0]
    month = date_elem_list[1]
    month_num = month_to_num[month]
    year = date_elem_list[2]
    hour = date_elem_list[3]
    prev_hour = (int(hour.lstrip('0')) - 1)%24
    f_prev_hour = f'{prev_hour:02}'

    query = """
        select addressidentifier, count(*) from TR_LREP
        where EVENTTIME between
            to_date('{0}-{1}-{02} {3}00','dd-mon-yyyy hh24mi')
            and
            to_date('{0}-{1}-{02} {3}59','dd-mon-yyyy hh24mi')
        group by addressidentifier
        """.format(day, month, year, f_prev_hour)

    try:
        qresult = ExecuteQuery(query, db_elem_list)
    except:
        alert.append('An exception returned from attempting a query. Likely, the database is inaccessable.')
        return alert

    if len(qresult) <= 0:
        alert.append('No data was returned when performing a query against the db.')
        return alert

    if qresult[0] == -1:
        for a in range(1, len(qresult)):
            alert.append(qresult[a])
        return alert

    # If call specified formatting for api we format and return here
    if apiFormatted:
        retval = []
        for qvalue in qresult:
            tag = 'CHANGE_ME_TO_CUSTOMER_4CHAR_TAG'
            minute = 0
            retval.append("{0};{1};{2};{3};{4};{5};{6};{7}".format(tag, qvalue[0], qvalue[1], minute, f_prev_hour, day, month_num, year))
        return retval

    # TODO:
    # Could use a qresult sanity check here to ensure value is not bonkers and looks like what we expect it to look like.
    return qresult


def ExecuteQuery(query, db_elem_list):
    """ This guy executes our query and returns the result.
        Return format is list of tuples e.g. [(14,)]
    """
    DB_USER = db_elem_list[0]
    DB_PASS = db_elem_list[1]
    DB_INSTANCE_NAME = db_elem_list[2]
    qresult = []

    try:
        with cx_Oracle.connect(DB_USER,DB_PASS,DB_INSTANCE_NAME) as connection:
            #connection.calltimeout = 3000 -- timeout in milliseconds -- only valid for 18c and higher.
            cursor = connection.cursor()
            cursor.execute(query)
            for r in cursor.fetchall():
                qresult.append(r)
    except Exception as e:
        qresult = [-1]
        qresult.append(f'An unexpected exception occurred while connecting to the target database: {e}')

    return qresult


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
        $python3 query_lrepCount.py --date 04-Dec-2019-10 --orastring "LBND07_TS_TRACKING;LBND07_TS_TRACKING;SWDB-ORACLE00"
    """
    args = GetArgs()
    result = DbGetLocationReports(args.date, args.orastring)
    for elem in result:
        print(elem)
    if result[0] != 'problem':
        TransmitToMaster(result)
