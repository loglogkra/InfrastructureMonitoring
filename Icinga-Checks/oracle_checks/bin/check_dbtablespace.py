#!/usr/bin/python3.8

import sys
import argparse
import cx_Oracle


RETURN_OK = 0
RETURN_WARN = 1
RETURN_CRITICAL = 2
RETURN_UNKNOWN = 3

"""
Description:
    Checks tablespaces for remaining capacity.
    Requires a user account with elevated permissions capable of running the query used.
Assumptions:
    The account credentials passed to this check are of a user that has adequite permissions to run the query that checks the tablespaces.
Expected use:
    This script is called by Icinga targeting an appropriate db instance.
Expected argument input:
    $python3 check_dbtablespace.py --dbuser SYS --dbpassword SYSPASSWORD --dbinstance WCS
Expected return value (good case):
    return: sys.exit(0)
    This tells Icinga 'OK'
Expected return value (bad case):
    return: sys.exit(2)
"""


def Check_TablespaceCapacity(db_user, db_pass, db_inst):
    ''' Tablespace capacity.
        Return from query looks like this:
            [(SYSAUX,75.87)
            (SYSTEM,12)
            (HIST_DATA,56.44)
            (USER_INDEX,37.38)
            (USER_DATA,22.01)
            (HIST_INDEX,39.37)
            (UNDOTBS1,50.43)
            (TEMP,0.27)]
    '''

    query = """
            select
                a.tablespace_name,
                round((a.bytes_alloc - nvl(b.bytes_free, 0)) * 100 / maxbytes, 2) pct_max_used
            from
            (
                select
                    f.tablespace_name,
                    sum(f.bytes) bytes_alloc,
                    sum(decode(f.autoextensible, 'YES',f.maxbytes,'NO', f.bytes)) maxbytes
                from
                    dba_data_files f
                group by
                    tablespace_name
            ) a,
            (
                select
                    ts.name tablespace_name,
                    sum(fs.blocks) * ts.blocksize bytes_free
                from
                    DBA_LMT_FREE_SPACE fs, sys.ts$ ts
                where
                    ts.ts# = fs.tablespace_id
                group by
                    ts.name, ts.blocksize
            ) b,
            dba_tablespaces c
            where
                a.tablespace_name = b.tablespace_name (+)
            and
                a.tablespace_name = c.tablespace_name
            and
                a.tablespace_name not like 'UNDO%'
            union all
            select
                h.tablespace_name,
                round(sum(nvl(p.bytes_used, 0)) * 100 / sum(decode(f.autoextensible, 'YES', f.maxbytes, 'NO', f.bytes)), 2) pct_max_used
            from
                sys.v_$TEMP_SPACE_HEADER h,
                sys.v_$Temp_extent_pool p,
                dba_temp_files f,
                dba_tablespaces c
            where
                p.file_id(+) = h.file_id
            and
                p.tablespace_name(+) = h.tablespace_name
            and
                f.file_id = h.file_id
            and
                f.tablespace_name = h.tablespace_name
            and
                f.tablespace_name = c.tablespace_name
            group by
                h.tablespace_name
        """

    qresult = []

    try:
        # Note: this query is ran with SYSDBA role
        with cx_Oracle.connect(db_user,db_pass,db_inst, mode=cx_Oracle.SYSDBA) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            for r in cursor.fetchall():
                qresult.append(r)
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
    parser.add_argument('-t', '--threashold', required=True, action='store', type=int,
                       help='Tablespace usage threashold. Tablespaces exceeding this percentage will trigger alerts.')
    args = parser.parse_args()
    return args


def main(dbuser, dbpass, db_inst, threashold):
    """ Samples:
        $python3 check_dbcleaner.py --dbuser user1 --dbpassword pass1 --dbinstance WCS
        $python3 check_dbcleaner.py --dbuser user1 --dbpassword pass1 --dbinstance 1.2.3.4/WCS.tgw.local
    """

    results = []
    retval = 0
    ukn_flag = False
    warn_flag = False
    crit_flag = False
    ok_flag = True

    # Failed calls to Check_TablespaceCapacity result in retval of '-1'
    result = Check_TablespaceCapacity(dbuser, dbpass, db_inst)

    if len(result) <= 0:
        results.append(f"Tablespace query failed to retun any values. User: {dbuser}, DB: {db_inst}")
        ukn_flag = True
        ok_flag = False

    if result[0] == -1:
        results.append(f"Tablespace query attempt was met with exception. User: {dbuser}, DB: {db_inst}")
        for elem in result:
            print(elem)
        ukn_flag = True
        ok_flag = False

    # Do not evaluate results if we got no results or erronious results.
    if ok_flag:
        # Create a list of naughty tablespaces violating/exceeding threashold
        try:
            xresult = [q for q in result if int(q[:][1]) > threashold]
        except ValueError:
            results.append('An unexpected value was returned preventing this check from proceeding. Please evaluate check and cause of exception.')
            print(result)
            ukn_flag = True
            ok_flag = False

    # Do not evaluate results if we got no results or erronious results.
    if ok_flag:
        if len(xresult) > 0:
            # Our list of naughty tablespaces has any names!
            results.append('Overfull tablespace(s)!')
            for x in xresult:
                results.append(f'\'{x[0]}\' is at \'{x[1]}%\' of its max capacity.')
            crit_flag = True
            ok_flag = False
        else:
            results.append('Healthy tablespaces. Everything OK.')
            # Our list of naughty tablespaces is empty. Print healthy capacity.
            for x in result:
                results.append(f'\'{x[0]}\' is at \'{x[1]}%\' of its max capacity.')

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
    retval = main(args.dbuser, args.dbpassword, args.dbinstance, args.threashold)
    sys.exit(retval)
