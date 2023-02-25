#!/usr/bin/python3.8

import sys
import argparse
import pymongo              # Will require pip install driver
import urllib
import datetime

RETURN_OK = 0
RETURN_WARN = 1
RETURN_CRITICAL = 2
RETURN_UNKNOWN = 3

"""
----------------------
Overview & Goal
----------------------
Check for workflows against a target Mongo database collection for select workflow names that are in a status 'Persisted' > x amount of time.
This means the workflow has stopped firing and will not resolve without human interaction.


----------------------
Expectations & Assumptions
----------------------
The target database, schema, users, collection, and tables exist and is reachable.


----------------------
Usage
----------------------
Script is called standalone or by the Icinga master node if so configured.
Delimited list of workflow names are expected and query results will yeild any record that is contained in the provided set.

examples:
$python3 check_wf_persisted.py --dbuser USER1 --dbpassword USER1PASS --ipaddress 0.0.0.0 --database RECOVER --collection WFINSTDATA --workflows "WF1;WF2;WF99"


----------------------
Return
----------------------
good case:
    print nothing (nothing returned from query)
    return: sys.exit(0) == sys.exit(RETURN_OK)

bad case:
    print query results (query returned matching workflow records that are in target state)
    return: sys.exit(2) == sys.exit(RETURN_CRITICAL)
"""


def ExecuteQuery(dbuser, dbpass, dbipaddress, database, collection, workflows):
    # TODO: Scrub input values for unexepected values, characters, and lengths.
    username = urllib.parse.quote_plus(dbuser)
    password = urllib.parse.quote_plus(dbpass)
    ipaddress = urllib.parse.quote_plus(dbipaddress)
    clientConnection = pymongo.MongoClient('mongodb://%s:%s@%s:27017/?authSource=admin' % (username, password,ipaddress))
    mydb = clientConnection[database]
    mycol = mydb[collection]
    filter = {"Status":"Persisted","DefinitionId":{"$in":workflows.split(';')},"LastUpdated":{"$lt":datetime.datetime.utcnow()-datetime.timedelta(minutes=10)}}

    retval = []

    try:
        qresult = [a for a in mycol.find(filter)]
        retval.append(len(qresult))
        for record in qresult:
            retval.append(record)
    except Exception as e:
        retval = [-1]
        retval.append(f'An unexpected exception occurred while connecting to the target database: {e}')

    return retval


def GetArgs():
    # Note: Do not create a '-h' flag, this is default '--help'
    parser = argparse.ArgumentParser(
             description='Command arguments.')
    parser.add_argument('-u', '--dbuser', required=True, action='store',
                       help='Database user name.')
    parser.add_argument('-p', '--dbpassword', required=True, action='store',
                       help='Database user password.')
    parser.add_argument('-i', '--ipaddress', required=True, action='store',
                       help='Accessable Mongo host IP address.')
    parser.add_argument('-d', '--database', required=True, action='store',
                       help='Target Mongo database name.')
    parser.add_argument('-c', '--collection', required=True, action='store',
                       help='Target Mongo database collection.')
    parser.add_argument('-w', '--workflows', required=True, action='store',
                       help='Semicolon delimited list of workflow names to filter.')
    args = parser.parse_args()
    return args


def main(dbuser, dbpass, ipaddress, database, collection, workflows):
    results = []
    ukn_flag = False
    warn_flag = False
    crit_flag = False
    ok_flag = False

    # When our target issue is positively detected, this is the response we expect to provide.
    # This string is customized specific to this check.
    expected_issue_response = "Persisted Workflows have been detected. Please clean up and correct underlying issue."

    # Peform the check!
    result = ExecuteQuery(dbuser, dbpass, ipaddress, database, collection, workflows)

    # Evaluate the result
    if len(result) <= 0:
        results.append(f"Check execution exception was caught. Please re-evaluate this check. {dbuser}, {ipaddress}")
        ukn_flag = True
        result = [-1]   # An empty return value cannot be evaluated. We overwrite the return value here.

    if result[0] == -1:
        results.append(f"Query to the database returned exception preventing check evaluation. Please troubleshoot database and connection. {dbuser}, {ipaddress}")
        ukn_flag = True

    if int(result[0]) > 0:
        results.append(f"{expected_issue_response} Count:{result[0]}, SCHEMA:{dbuser}, INSTANCE:{ipaddress}")
        for r in result:
            results.append(r)
        crit_flag = True
        #warn_flag = True

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
    retval = main(args.dbuser, args.dbpassword, args.ipaddress, args.database, args.collection, args.workflows)
    sys.exit(retval)
