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
----------------------
Overview & Goal
----------------------
Checks for planning orders that were canceled w/o any reason provided.
This event should never happen at a customer site.

----------------------
Expectations & Assumptions
----------------------
The target database, schema, and tables exist.
The SQL statement will be ran as the same user as provided by the arguments. This user is expected to be the same target schema.
e.g. a query for PROD_SIS will be exectued as user PROD_SIS, not any other user such as SYS or TGW_MONITORING.


----------------------
Usage
----------------------
Script is called as an individual check configured by the Icinga master node.
Multiple users/schemas can be passed to run the same check for the same instance, but for each schema.

examples:
$python3 check_cancelledplanningorder.py --dbuser user1 --dbpassword user1pass --dbinstance SWDB-ORACLE99
$python3 check_cancelledplanningorder.py --dbuser user1;user2 --dbpassword user1pass;user2pass --dbinstance WCS
$python3 check_cancelledplanningorder.py --dbuser user1;user2;user3 --dbpassword user1pass;user2pass;user3pass --dbinstance 1.2.3.4/WCS.tgw.local


----------------------
Return
----------------------
good case:
    return: sys.exit(0) == sys.exit(RETURN_OK)

bad case:
    return: sys.exit(2) == sys.exit(RETURN_CRITICAL)
"""


def ExecuteQuery(db_user, db_pass, db_inst):
    query = """
        select count(*)
        from {0}.order_line ol2
        join PLANNINGORDERLINE_ATTRIBUTES pola
          on pola.ENTITY_ID = ol2.ID
          and ol2.ORDER_LINE_STATUS = -304
          and (pola.REASON is null or pola.reason = '')
        and ol2.modified > current_timestamp - interval '25' hour
        """.format(db_user)

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
    results = []
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
        result = ExecuteQuery(user_list[i], pass_list[i], db_inst)

        if len(result) <= 0:
            results.append(f"No data exists for when query was performed. {user_list[i]}, {db_inst}")
            ukn_flag = True

        if result[0] == -1:
            results.append(f"Check execution exception was caught. {user_list[i]}, {db_inst}")
            for elem in result:
                print(elem)
            ukn_flag = True

        if int(result[0]) > 0:
            results.append(f"Planning orders cancelled without reason have been detected. {user_list[i]}, {db_inst}")
            #crit_flag = True
            warn_flag = True

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