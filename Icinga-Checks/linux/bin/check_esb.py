#!/usr/local/bin/python3.6

import sys
import cx_Oracle


"""
----------------------
Overview & Goal
----------------------
Check the ESBtransfer table for any transmission failures.


----------------------
Expectations & Assumptions
----------------------
This script is called by Icinga.

Argument input: 
No command line arguments necessary. 
Check will always look for any deficiencies. 


----------------------
Steps
----------------------
Parse input arguments
Query database for status 92 counts.
If count > 0, deficiency detected.


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


def HandleRunQuery():    
    DB_USER = 'PROD_HGW'
    DB_PASS = 'PROD_HGW'
    DB_INSTANCE_NAME = 'WCS'
    qresult = []
    query = """
            select count(*) from esbtransfer where state = 92
        """
        
    '''
    Removed because this is not running as sysdba
    with cx_Oracle.connect(DB_USER,DB_PASS,DB_INSTANCE_NAME, mode=cx_Oracle.SYSDBA) as connection:
    '''

    try:
        with cx_Oracle.connect(DB_USER,DB_PASS,DB_INSTANCE_NAME) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            for r in cursor.fetchall():
                qresult.append(r)
    except Exception as e:
        print(f'An unexpected exception occurred while connecting to the target database: {e}')
        
    # Debug
    '''
    for q in qresult:
        print(q)
    print(len(qresult))
    '''
    if int(qresult[0][0]) > 0:
        print(f'Host Gateway message transmission (error code 92) failure detected. Error count: {qresult[0][0]} ')
        return False


    return True


def Main():
    if HandleRunQuery():
        sys.exit(RETURN_OK)
    else:
        sys.exit(RETURN_CRITICAL)


if __name__ == '__main__':
    """
    python3.6 check_esb.py_
    """
    
    Main()
