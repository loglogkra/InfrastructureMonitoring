import cx_Oracle


def CheckDbStatus(db_check_positive):
    '''Database is mounted and open.
    '''

    alert = ['Database instance is not OPEN and ACTIVE.']
    qresult = []
    query = """
        select
            status,
            database_status
        from V$INSTANCE
        """

    try:
        qresult = ExecuteQuery(query)
    except:
        alert.append('An exception returned from attempting a query. Likely, the database is inaccessable. Check: CheckDbStatus') 
        return alert
        
    if len(qresult) <= 0:
        alert.append('No data was returned when performing a query against the db.')
        return alert

    if qresult[0] == -1:
        for a in range(1, len(qresult)):
            alert.append(qresult[a])
        return alert

    if qresult[0][0] == 'OPEN':
        if qresult[0][1] == 'ACTIVE':
            return [db_check_positive]

    return qresult


def ExecuteQuery(query):
    # TODO! Credentials should come from the master node in a variable
    # credentials and instance names may change from site to site.
    DB_USER = 'sys'
    DB_PASS = 'ek_sal_dit_koop'
    DB_INSTANCE_NAME = 'WCS'
    # time_out = 1000  # milliseconds -- TODO: use this!
    qresult = []

    try:
        with cx_Oracle.connect(DB_USER,DB_PASS,DB_INSTANCE_NAME, mode=cx_Oracle.SYSDBA) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            for r in cursor.fetchall():
                qresult.append(r)
    except Exception as e:
        qresult = [-1]
        qresult.append(f'An unexpected exception occurred while connecting to the target database: {e}')

    return qresult
