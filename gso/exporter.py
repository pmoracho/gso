import pyodbc
from gso.tabulate import tabulate

SQL_dbases = """
select name
       from sys.databases
       where 1 = 1
             {where_dbases}
    order by name
"""

SQL_moudlos = """
set nocount on;
use {base};

set nocount off;
select
    '{server}',
	[db] = db_name(),
	[schema] = OBJECT_SCHEMA_NAME(m.object_id),
	[name] = OBJECT_NAME(m.object_id),
    o.type,
    o.type_desc,
    m.uses_ansi_nulls,
    m.uses_quoted_identifier,
    o.create_date,
    o.modify_date,
    m.definition
    from	sys.sql_modules m
    inner join sys.objects o
        on m.object_id = o.object_id
    where 1=1
	      {where}
    order by
	    o.type;
"""

def export(cfg, object_pattern):

    servers = []
    columns = []
    objetos = []

    tipo, server, base, owner, obj = get_parts_from_object_patter(object_pattern)

    if server == '*':
        servers = list(cfg.servers)
    else:
        servers.append(server)

    where_dbases = ""
    if base != '*':
        where_dbases = where_dbases + "   AND  name LIKE '%" + base + "%'"

    where = ""
    if obj != '*':
        where = where + "   AND  OBJECT_NAME(m.object_id) LIKE '%" + obj + "%'"

    if owner != '*':
        where = where + "   AND  OBJECT_SCHEMA_NAME(m.object_id) LIKE '%" + owner + "%'"

    if tipo != '*':
        # IF, FN, p, TF, V
        where = where + "   AND  o.type LIKE '%" + tipo + "%'"

    for server in servers:
        print(server)
        connectstr = cfg.servers[server]
        cnxn = pyodbc.connect(connectstr)
        cursor = cnxn.cursor()

        SQL = SQL_dbases.replace('{where_dbases}', where_dbases)
        cursor.execute(SQL)

        for base in [row[0] for row in cursor.fetchall()]:
            print(base)

            SQL = SQL_moudlos.replace('{base}', base).replace('{server}', server).replace('{where}', where)

            print(SQL)
            cursorb = cnxn.cursor()
            cursorb.execute(SQL)
            cursorb.nextset()
            #columns = [column[0] for column in cursorb.description]
            results = [row for row in cursorb.fetchall()]
            objetos.extend(results)

    tablestr = tabulate(
                        tabular_data		= objetos,
                        headers				= columns,
                        tablefmt			= "psql",
                        stralign			= "left"
            )

    print(tablestr)


def get_parts_from_object_patter(object_pattern):
    return tuple(object_pattern.split('.'))
