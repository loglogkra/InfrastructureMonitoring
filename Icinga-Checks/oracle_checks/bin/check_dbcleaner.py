#!/usr/bin/python3.8

import sys
import argparse
from datetime import date
import cx_Oracle


RETURN_OK = 0
RETURN_WARN = 1
RETURN_CRITICAL = 2
RETURN_UNKNOWN = 3

"""
Description:
    Checks the db cleaner log for errors in the most recent execution of the db cleaner.
    Checks for 'the most recent' set of db cleaner logs.
    Will fail if no logs are present for the current day.
    Cannot detect logs that should exist, but were omitted from the database.
    Able to check one or more schemas on the same instance.
    Checking different instances is not possible with this script. Concider a separate check, treating instances like hosts.
Assumptions:
    The DB cleaner log must exist for the user and user password provided.
    The DB cleaner log adheres to the standard naming convention i.e DB_CLEANER_LOG
    The DB cleaner may be running while this check is performed, resulting in false-positive.
Expected use:
    This script is called by Icinga after install of syshealth pkg.
Expected argument input:
    $python3 check_dbcleaner.py --dbuser SYS --dbpassword SYSPASSWORD --dbinstance WCS
Expected return value (good case):
    return: sys.exit(0)
    This tells Icinga 'OK'
Expected return value (bad case):
    return: sys.exit(2)
"""


def Check_DBCleaner(db_user, db_pass, db_inst):
    today = date.today()
    year = today.strftime("%Y")
    month = today.strftime("%b")
    day = today.strftime("%d")

    query = """
        select count(*) from {0}.DB_CLEANER_LOG
        where eventtime > to_date('{1}-{2}-{3} 0001','yyyy-mon-dd hh24mi')
        and
        cleanerlogtyp = 'DBCLEANERROR'
        """.format(db_user, year, month, day)

    qresult = []

    try:
        with cx_Oracle.connect(db_user,db_pass,db_inst) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            for r in cursor.fetchall():
                qresult.append(r[0])
    except Exception as e:
        qresult = [-1]
        qresult.append(f'An unexpected exception occurred while connecting to the target database: {e}')

    return qresult


def GetArgs():
    # Note: Do not create a '-h' flag, this is default '--help'
    parser = argparse.ArgumentParser(
             description='Process args for online backup log duration.')
    parser.add_argument('-u', '--dbuser', required=True, action='store',
                       help='Database user name list semi-colon delimited.')
    parser.add_argument('-p', '--dbpassword', required=True, action='store',
                       help='Database user password list semi-colon delimited.')
    parser.add_argument('-i', '--dbinstance', required=True, action='store',
                       help='Database instance name.')
    args = parser.parse_args()
    return args


def main(dbuser, dbpass, db_inst):
    """ Samples:
        $python3 check_dbcleaner.py --dbuser user1 --dbpassword PROD_PASSWORD --dbinstance WCS_INSTANCE
        $python3 check_dbcleaner.py --dbuser user1;user2 --dbpassword pass1;pass2 --dbinstance WCS
        $python3 check_dbcleaner.py --dbuser user1;user2;user3 --dbpassword pass1;pass2;pass3 --dbinstance 1.2.3.4/WCS.tgw.local
    """

    results = []
    retval = 0
    ukn_flag = False
    warn_flag = False
    crit_flag = False
    ok_flag = False

    user_list = dbuser.split(';')
    pass_list = dbpass.split(';')

    if len(user_list) != len(pass_list):
        print("Bad check configuration. The count of schemas to check does not match the count of schema-passwords.")
        return RETURN_UNKNOWN

    for i in range(0, len(user_list)):
        result = ""
        result = Check_DBCleaner(user_list[i], pass_list[i], db_inst)

        if len(result) <= 0:
            results.append(f"No data exists for when query was performed. {user_list[i]}, {db_inst}")
            ukn_flag = True

        if result[0] == -1:
            results.append(f"Check execution exception was caught. {user_list[i]}, {db_inst}")
            for elem in result:
                print(elem)
            ukn_flag = True

        if int(result[0]) > 0:
            results.append(f"A failure was detected in the DB_CLEANER_LOG. {user_list[i]}, {db_inst}")
            crit_flag = True

        if int(result[0]) == 0:
            ok_flag = True

    # Output all results
    for r in results:
        print(r)

    # Return the most important return value
    if (crit_flag):
        return RETURN_CRITICAL

    if (warn_flag):
        return RETURN_WARN

    if (ukn_flag):
        return RETURN_UNKNOWN

    if (ok_flag):
        return RETURN_OK

    # Should not get here if script is OK
    print("No return value flagged from check. Re-evaluate this check.")
    return RETURN_UNKNOWN



if __name__ == '__main__':
    args = GetArgs()
    retval = main(args.dbuser, args.dbpassword, args.dbinstance)
    sys.exit(retval)
