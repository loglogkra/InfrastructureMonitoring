import cx_Oracle


def CheckRecoveryFileDest(db_check_positive):
    '''Recovery file capacity.
    '''

    alert = []
    qresult = []
    query = """
        select
            round(space_used * 100 / space_limit, 2) pct_used_space
        from V$RECOVERY_FILE_DEST
        """

    try:
        qresult = ExecuteQuery(query)
    except:
        alert.append('An exception returned from attempting a query. Likely, the database is inaccessable. Check: CheckRecoveryFileDest')      
        return alert
        
    if len(qresult) <= 0:
        alert.append('No data was returned when performing a query against the db.')
        return alert

    if qresult[0] == -1:
        for a in range(1, len(qresult)):
            alert.append(qresult[a])
        return alert
    try:
        xresult = [q for q in qresult if int(q[0]) > 85]
    except ValueError:
        alert.append('An unexpected value was returned. Query evaluation is required. Query result: ')
        for elem in xresult:
            alert.append(elem)
        
    if len(xresult) > 0:
        alert.append(f'Recovery file size is at: \'{xresult[0][0]}\'% of its max capacity.')
    else:
        return [db_check_positive]

    return alert


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
