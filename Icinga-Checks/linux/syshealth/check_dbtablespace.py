import cx_Oracle


def CheckTsCapacity(db_check_positive):
    '''Tablespace capacity.
        TODO: Isolate this check from the other Oracle checks.
        Allow for configuration to be set from the HostAgent.py file.
        Make comparable to the Disk Checks.

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

    alert = []
    qresult = []
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

    try:
        qresult = ExecuteQuery(query)
    except:
        alert.append('An exception returned from attempting a query. Likely, the database is inaccessable. Check: CheckTsCapacity') 
        return alert
        
    if len(qresult) <= 0:
        alert.append('No data was returned when performing a query against the db.')
        return alert

    if qresult[0] == -1:
        for a in range(1, len(qresult)):
            alert.append(qresult[a])
        return alert
    try:
        xresult = [q for q in qresult if int(q[:][1]) > 90]
    except ValueError:
        alert.append('An unexpected value was returned. Query evaluation is required. Query result: ')
        for elem in xresult:
            alert.append(elem)     

    if len(xresult) > 0:
        for x in xresult:
            alert.append(f'Tablespace \'{x[0]}\' is at \'{x[1]}%\' of its max capacity.');
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
