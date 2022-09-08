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

SQL_Tables = """
set nocount on;
use [{base}];

set nocount off;
SELECT	[objz].[name],
        [objz].[object_id],
        SCHEMA_NAME([objz].[schema_id])
        FROM .[sys].[objects] AS [objz]
        WHERE 	[objz].[type]  IN ('S','U')
                AND [objz].[name]  <>  'dtproperties'
        order by [objz].[name]
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
    CASE WHEN o.type = 'P ' AND CHARINDEX('_1_0_0',  OBJECT_NAME(m.object_id)) > 0 THEN 'PV' ELSE o.type END,
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
    'PV': 'spv',
    'V ': 'view',
    'FN': 'fn',
    'IF': 'fn',
    'TR': 'trg',
    'R ': 'rule',
    'TF': 'fn',
    'D ': 'dft',
    'TB': 'tbl'
}

type_obj = {v: k for k, v in obj_type.items()}


def export(cfg, object_pattern):

    objetos = get_objects(cfg, object_pattern)
    i = 0
    t = len(objetos)

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]

    bar = ProgressBar(widgets=widgets, maxval=t)

    for s, base, owner, obj, tipo, _, _, _, _, _, text in objetos:
        widgets[0] = FormatLabel('[{0}]'.format(obj.ljust(50)[:50]))
        path = os.path.join(cfg.export_path, base, obj_type[tipo]).lower()
        file = os.path.join(path, owner + '.' + obj + '.sql')
        if text:
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)

            exports[tipo](base, owner, obj, path, file, text)
        i = i + 1
        bar.update(i)
    bar.finish()

def export_content(base, owner, obj, path, file, text):
    text = [l for l in text.split('\r')]
    save_object(file, text)

def export_sp(base, owner, obj, path, file, text):

    searchtxt = "CREATE PROCEDURE " + obj
    replacetxt = "CREATE PROCEDURE [" + owner + "].[" + obj + "]"

    text = get_set_header(base) + text.replace(searchtxt, replacetxt)
    text = [l for l in text.split('\r')]
    save_object(file, text)

def export_function(base, owner, obj, path, file, text):

    text = get_set_header(base) + text
    text = [l for l in text.split('\r')]
    save_object(file, text)

def export_table(base, owner, obj, path, file, text):
    pass

def save_object(file, text):
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(text)

def get_set_header(base):
    return """USE [{base}]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

""".replace('{base}', base)

exports = {
    'P ': export_sp,
    'PV': export_sp,
    'V ': export_content,
    'FN': export_function,
    'IF': export_function,
    'TR': export_content,
    'R ': export_content,
    'TF': export_function,
    'TB': export_table,
    'D ': export_content
}

def get_objects(cfg, object_pattern):

    servers = []
    columns = []
    objetos = []

    tipo, server, base, owner, objname = get_parts_from_object_patter(object_pattern)

    if server == '*':
        servers = list(cfg.servers)
    else:
        servers.append(server)

    where_dbases = "" if base == '*' else "   AND  name LIKE '%" + base + "%'"

    where = ""
    if objname != '*':
        where = where + "   AND  OBJECT_NAME(m.object_id) LIKE '%" + objname + "%'"

    if owner != '*':
        where = where + "   AND  OBJECT_SCHEMA_NAME(m.object_id) LIKE '%" + owner + "%'"

    if tipo != '*':
        if tipo != 'TB':
            # IF, FN, p, TF, V
            where = where + "   AND  o.type LIKE '%" + type_obj[tipo] + "%'"
        else:
            # Invalidamos la consulta, las tablas van por otro camino
            where = where + "   AND 1 = 2"

    for server in servers:

        connectstr = cfg.servers[server]
        cnxn = pyodbc.connect(connectstr)
        cursor = cnxn.cursor()

        SQL = SQL_dbases.replace('{where_dbases}', where_dbases)
        cursor.execute(SQL)

        for base in [row[0] for row in cursor.fetchall()]:
            # Objetos en Modulos
            objetos.extend(get_modulos(cnxn, server, base, where))

            # Tablas
            objetos.extend(get_tables(cnxn, server, base, objname))


    return objetos

def get_parts_from_object_patter(object_pattern):
    return tuple(object_pattern.split('.'))

def get_modulos(cnxn, server, base, where):
    SQL = SQL_moudlos.replace('{base}', base).replace('{server}', server).replace('{where}', where)
    cursorb = cnxn.cursor()
    cursorb.execute(SQL)
    cursorb.nextset()
    return [row for row in cursorb.fetchall()]

def get_tables(cnxn, server, base, objname):
    return []