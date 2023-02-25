#!/usr/local/bin/python3.6

import sys
import argparse
import re
import cx_Oracle


"""
----------------------
Overview & Goal
----------------------
Check the most reacent record of execution time for all provided SQL IDs.


----------------------
Expectations & Assumptions
----------------------
This script is called by Icinga.

Argument input: 
    -s := list of sql ids paired with their threashold value in msec
    e.g. -s "sqlidaaaa:1000;sqlidffff:10" 
        sql_id 'sqlidaaaa' should always finish under 1000ms
        sql_id 'sqlidffff' should always finish under 10ms


----------------------
Steps
----------------------
Parse input arguments
For each SQL ID assign to bind variable and run query
Compare return variables against threashold values


----------------------
Return
----------------------
Good case: sys.exit(0)
    This tells Icinga 'OK'
    
Bad case: sys.exit(2) and stdout message
    sys.exit(2) tells Icinga 'Critical'.
    Output to stdout is returned to the master node.
"""

RETURN_OK = 0
RETURN_WARN = 1
RETURN_CRITICAL = 2


def HandleRunQuery(sql_id, time_threadhold):    
    DB_USER = 'sys'
    DB_PASS = 'ek_sal_dit_koop'
    DB_INSTANCE_NAME = 'WCS'
    qresult = []
    query = """
        select msec_avg_elapsed
            from 
            (
                select 
                  ROUND(elapsed_time/executions/1000) msec_avg_elapsed
                from v$sql 
                where sql_id = :sql_id
                and executions > 0
                order by last_active_time desc
            ) 
            where rownum = 1
        """
        
    '''
    Removed because this is not running as sysdba
    with cx_Oracle.connect(DB_USER,DB_PASS,DB_INSTANCE_NAME, mode=cx_Oracle.SYSDBA) as connection:
    '''

    try:
        with cx_Oracle.connect(DB_USER,DB_PASS,DB_INSTANCE_NAME, mode=cx_Oracle.SYSDBA) as connection:
            cursor = connection.cursor()
            cursor.execute(query, sql_id=sql_id)
            for r in cursor.fetchall():
                qresult.append(r)
    except Exception as e:
        print(f'An unexpected exception occurred while connecting to the target database: {e}')
        
    # Debug
    print(qresult)
    print(len(qresult))
    
    # We return True, because it is not an issue if there is no returned query.
    # We do print the result for awareness.
    if len(qresult) != 1:
        print('No record of this SQL_ID was found: ' + sql_id)      
        return True

    if int(qresult[0][0]) < int(time_threadhold):
        print(f'{sql_id} : {qresult[0][0]}ms')
        return True


    # Not having already returned, we assume failure. 
    print(f'Query {sql_id} ran above threashold of {time_threadhold}.')  
    return False


def Main(args):
    all_queries_ok = True
    
    for one_query_tuple in args.sql.split(';'):
        bindvar = one_query_tuple.split(':')
        if len(bindvar) != 2:
            sys.exit(RETURN_WARN)
    
        all_queries_ok = all_queries_ok and HandleRunQuery(bindvar[0], bindvar[1])

    if all_queries_ok:
        sys.exit(RETURN_OK)
    else:
        sys.exit(RETURN_CRITICAL)

def GetArgs():
    parser = argparse.ArgumentParser(
             description='Process input arguments for this script.')
    parser.add_argument('-s', '--sql', required=True, action='store',
                       help='SQL ID and threashold time, colon delimited. Additional tuples must be semi-colon delimted.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    """
    python3.6 check_sql.py -s "154q4bwr2jpby:1000;154q4bwr2jpby:800"
    """
    args = GetArgs()  
    Main(args)