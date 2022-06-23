import pyodbc
import os
from pathlib import Path
from gso.tabulate import tabulate

from progressbar import ProgressBar
from progressbar import FormatLabel
from progressbar import Percentage
from progressbar import Bar
from progressbar import RotatingMarker
from progressbar import ETA

SQL_dbases = """
select name
       from sys.databases
       where    1 = 1
                {where_dbases}
    order by name
"""

SQL_moudlos = """
set nocount on;
use [{base}];

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
    where   1=1
	      {where}
    order by
	    o.type;
"""

obj_type = {
    'P ': 'sp',
    'V ': 'view',
    'FN': 'fn',
    'IF': 'fn',
    'TR': 'trg',
    'R ': 'rule',
    'TF': 'fn',
    'D ': 'dft'
}

type_obj = {v: k for k, v in obj_type.items()}



def export(cfg, object_pattern):

    objetos = get_objects(cfg, object_pattern)
    i = 0
    t = len(objetos)

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]

    bar = ProgressBar(widgets=widgets, maxval=t)

    for s, b, o, obj, t, _, _, _, _, _, text in objetos:
        widgets[0] = FormatLabel('[{0}]'.format(obj.ljust(50)[:50]))
        path = os.path.join(cfg.export_path, b, obj_type[t]).lower()
        file = os.path.join(path, o + '.' + obj + '.sql')
        if text:
            exports[t](path, file, text)
        i = i + 1
        bar.update(i)
    bar.finish()

def export_content(path, file, text):
    # print("Exportando conenido: {0}".format(file))
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    text = [l for l in text.split('\r')]
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(text)

def export_sp(path, file, text):
    # print("Exportando SP: {0}".format(file))
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    text = [l for l in text.split('\r')]
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(text)

exports = {
    'P ': export_sp,
    'V ': export_content,
    'FN': export_content,
    'IF': export_content,
    'TR': export_content,
    'R ': export_content,
    'TF': export_content,
    'D ': export_content
}

def get_objects(cfg, object_pattern):

    servers = []
    columns = []
    objetos = []

    tipo, server, base, owner, obj = get_parts_from_object_patter(object_pattern)

    if server == '*':
        servers = list(cfg.servers)
    else:
        servers.append(server)

    where_dbases = "" if base == '*' else "   AND  name LIKE '%" + base + "%'"

    where = ""
    if obj != '*':
        where = where + "   AND  OBJECT_NAME(m.object_id) LIKE '%" + obj + "%'"

    if owner != '*':
        where = where + "   AND  OBJECT_SCHEMA_NAME(m.object_id) LIKE '%" + owner + "%'"

    if tipo != '*':
        # IF, FN, p, TF, V
        where = where + "   AND  o.type LIKE '%" + type_obj[tipo] + "%'"

    for server in servers:

        connectstr = cfg.servers[server]
        cnxn = pyodbc.connect(connectstr)
        cursor = cnxn.cursor()

        SQL = SQL_dbases.replace('{where_dbases}', where_dbases)
        cursor.execute(SQL)

        for base in [row[0] for row in cursor.fetchall()]:
            SQL = SQL_moudlos.replace('{base}', base).replace('{server}', server).replace('{where}', where)
            cursorb = cnxn.cursor()
            cursorb.execute(SQL)
            cursorb.nextset()
            results = [row for row in cursorb.fetchall()]
            objetos.extend(results)

    return objetos


def get_parts_from_object_patter(object_pattern):
    return tuple(object_pattern.split('.'))
