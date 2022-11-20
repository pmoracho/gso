import pyodbc
import os
from pathlib import Path
from gso.tabulate import tabulate
from gso.export_helpers import *
from gso.helper import slugify
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
SELECT	'{server}',
        [db] = db_name(),
        [schema] = OBJECT_SCHEMA_NAME([objz].[object_id]),
        [name] = REPLACE([objz].[name], '''', ''),
        'TB',
        NULL,
        NULL,
        NULL,
        NULL,
        CASE WHEN [objz].modify_date > [objz].create_date THEN [objz].modify_date ELSE [objz].create_date END,
        NULL
        FROM .[sys].[objects] AS [objz]
        WHERE 	[objz].[type]  IN ('U')
                AND [objz].[name]  <>  'dtproperties'
                AND db_name() NOT IN ('tempdb', 'master', 'model', 'msdb')
                AND {where}
        order by [objz].[name]
"""

SQL_modulos = """
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
    CASE WHEN o.modify_date > o.create_date THEN o.modify_date ELSE o.create_date END,
    m.definition
    from	sys.sql_modules m
    inner join sys.objects o
        on m.object_id = o.object_id
    where   1=1
	      {where}
    order by
	    o.type;
"""

objetos_def = {
    "P": {"folder": "sp", "export": export_sp, "name_format": "{owner}.{objname}"},
    "PV": {"folder": "spv", "export": export_sp, "name_format": "{owner}.{objname}"},
    "V": {"folder": "view", "export": export_content, "name_format": "{owner}.{objname}"},
    "FN": {"folder": "fn", "export": export_function, "name_format": "{owner}.{objname}"},
    "IF": {"folder": "fn", "export": export_function, "name_format": "{owner}.{objname}"},
    "TR": {"folder": "trg", "export": export_content, "name_format": "{owner}.{objname}"},
    "R": {"folder": "rule", "export": export_content, "name_format": "{owner}.{objname}"},
    "TF": {"folder": "trg", "export": export_function, "name_format": "{owner}.{objname}"},
    "D": {"folder": "trg", "export": export_content, "name_format": "{owner}.{objname}"},
    "TB": {"folder": "trg", "export": export_table, "name_format": "{owner}.{objname}"},
    "TablaTemporal": {"folder": "mobj\\tblt", "export": export_content, "name_format": "{objname}"},
    "Reporte": {"folder": "mobj\\rpt", "export": export_content, "name_format": "{objname}"},
    "Parametro": {"folder": "mobj\\pmt", "export": export_content, "name_format": "{objname}"},
    "ProcesosAgenda": {"folder": "mobj\\pa", "export": export_content, "name_format": "{objname}"},
    "Modulo": {"folder": "mobj\\mo", "export": export_content, "name_format": "{objname}"},
    "Operacion": {"folder": "mobj\\op", "export": export_content, "name_format": "{objname}"},
}

type_obj = {v["folder"]: k for k, v in objetos_def.items()}


def export(cfg, object_pattern, ndays=None):

    print("Creating list of objects (Tables/Code/Mecanus Objects)")
    objetos = get_objects(cfg, object_pattern, ndays)

    print("Exporting objects to files")
    i = 0
    t = len(objetos)

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]
    bar = ProgressBar(widgets=widgets, maxval=t)

    for s, base, owner, obj, tipo, _, _, _, _, _, text in objetos:
        objcompleto = base + "." + owner + "." + obj
        widgets[0] = FormatLabel('[{0}]'.format(objcompleto.ljust(80)[:80]))
        path = os.path.join(cfg.export_path, base, objetos_def[tipo]["folder"]).lower()

        file = objetos_def[tipo]["name_format"].replace("{owner}", owner).replace("{objname}", obj)
        file = os.path.join(path, slugify(file) + '.sql')

        if text:
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)
            objetos_def[tipo]["export"](base, owner, obj, path, file, text)
        i = i + 1
        bar.update(i)
    bar.finish()


def get_set_header(base):
    return """USE [{base}]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

""".replace('{base}', base)


def get_objects(cfg, object_pattern, ndays=None):

    servers = []
    columns = []
    objetos = []

    tipo, server_solicitado, base_solicitada, owner, objname = get_parts_from_object_pattern(object_pattern)

    if server_solicitado == '*':
        servers = list(cfg.servers)
    else:
        servers.append(server_solicitado)

    where = ""
    where_tables = "   1 = 1"
    if objname != '*':
        where = where + "   AND  OBJECT_NAME(m.object_id) LIKE '%" + objname + "%'"
        where_tables = where_tables + "   AND [objz].[name] LIKE '%" + objname + "%'"

    if owner != '*':
        where = where + "   AND  OBJECT_SCHEMA_NAME(m.object_id) LIKE '%" + owner + "%'"
        where_tables = where_tables + "   AND OBJECT_SCHEMA_NAME([objz].[object_id]) LIKE '%" + owner + "%'"

    if ndays:
        where = where + "   AND  datediff(day, CASE WHEN o.modify_date > o.create_date THEN o.modify_date ELSE o.create_date END, GETDATE()) <= {0}".format(ndays)
        where_tables = where_tables + "   AND  datediff(day, CASE WHEN [objz].modify_date > [objz].create_date THEN [objz].modify_date ELSE [objz].create_date END, GETDATE()) <= {0}".format(ndays)

    if tipo != '*':
        if tipo != 'TB':
            # IF, FN, p, TF, V
            where = where + "   AND  o.type LIKE '%" + type_obj[tipo] + "%'"
            where_tables = where_tables + "   AND 1 = 2"
        else:
            # Invalidamos la consulta, las tablas van por otro camino
            where = where + "   AND 1 = 2"

    for server in servers:

        Databases = None if server not in cfg.Databases else cfg.Databases[server]
        where_dbases = "" if base_solicitada == '*' else "   AND  name LIKE '%" + base_solicitada + "%'"
        where_dbases = where_dbases + "AND name IN ('" + "', '".join([e.strip() for e in Databases.split(',')]) + "')\n" if Databases else ""

        connectstr = cfg.servers[server]
        cnxn = pyodbc.connect(connectstr)
        cursor = cnxn.cursor()

        SQL = SQL_dbases.replace('{where_dbases}', where_dbases)

        cursor.execute(SQL)
        bases = [row[0] for row in cursor.fetchall()]
        cursor.close()

        for base in bases:
            # Objetos en Modulos
            # objetos.extend(get_modulos(cnxn, server, base, where))

            # Tablas
            # objetos.extend(get_tables(cnxn, server, base, where_tables))

            # Objetos Mecanus
            objetos.extend(get_objetos_mecanus(cnxn, server, base, where_tables))


    return objetos

def get_parts_from_object_pattern(object_pattern):
    return tuple(object_pattern.split('.'))

def get_modulos(cnxn, server, base, where):
    SQL = SQL_modulos.replace('{base}', base).replace('{server}', server).replace('{where}', where)
    cursorb = cnxn.cursor()
    cursorb.execute(SQL)
    cursorb.nextset()
    return [row for row in cursorb.fetchall()]

def get_objetos_mecanus(cnxn, server, base, where):

    SQL_MO = """
DECLARE @ErrorMessage	VARCHAR(2000)
EXEC [g-track].dbo.List_Mecanus_Objects
        @Database	    = '{base}',
        @TipoObjeto	    = NULL,
        @ErrorMessage	= @ErrorMessage OUTPUT
"""

    SQL = SQL_MO.replace('{base}', base).replace('{server}', server)
    cursorc = cnxn.cursor()
    #print(SQL)
    cursorc.execute(SQL)
    objetos_mecanus = cursorc.fetchall()
    cursorc.close()

    SQL_ddl = """
SET NOCOUNT ON
DECLARE @Script		   NVARCHAR(MAX)
DECLARE @ErrorMessage  VARCHAR(2000)

EXEC [g-track].dbo.Export_Mecanus_Object
		@Database	    = '{base}',
        @TipoObjeto     = '{tipo_objeto}',
		@ObjectId	    = '{objname}',
        @FlagGIT	    = 1,
        @FlagOnlyScript	= 1,
        @FilePath       = NULL,
		@Script		    = @Script OUTPUT,
		@ErrorMessage= @ErrorMessage OUTPUT;

SET NOCOUNT OFF
SELECT @Script
"""
    i = 0
    resultados = []
    t = len(objetos_mecanus)
    if t == 0:
        return resultados

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]

    bar = ProgressBar(widgets=widgets, maxval=t)
    cursorc = cnxn.cursor()
    for row in objetos_mecanus:
        owner, tipo_objeto, objname = row
        objcompleto = base + "." + objname
        widgets[0] = FormatLabel('[{0}]'.format(objcompleto.ljust(80)[:80]))
        SQL = SQL_ddl.replace('{base}', base).replace('{objname}', objname).replace('{tipo_objeto}', tipo_objeto)
        cursorc.execute(SQL)
        text = cursorc.fetchone()
        new_row = (server, base, owner, objname, tipo_objeto, None, None, None, None, None,  text[0])
        resultados.append(new_row)
        i = i + 1
        bar.update(i)
    bar.finish()
    return resultados

def get_tables(cnxn, server, base, where):

    SQL = SQL_Tables.replace('{base}', base).replace('{server}', server).replace('{where}', where)
    cursorb = cnxn.cursor()
    #print(SQL)
    cursorb.execute(SQL)
    cursorb.nextset()
    tablas = cursorb.fetchall()
    cursorb.close()

    SQL_ddl = """
SET NOCOUNT ON
DECLARE @Script		   VARCHAR(MAX)
DECLARE @ErrorMessage  VARCHAR(2000)

EXEC [g-track].dbo.SCRIPT_Mecanus_TablaFisica
		@Database	 = '{base}',
		@Owner		 = '{owner}',
		@ObjectId	 = '{objname}',
		@Script		 = @Script OUTPUT,
		@ErrorMessage= @ErrorMessage OUTPUT;

SET NOCOUNT OFF
SELECT @Script
"""
    i = 0
    resultados = []
    t = len(tablas)
    if t == 0:
        return resultados

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]

    bar = ProgressBar(widgets=widgets, maxval=t)
    cursorc = cnxn.cursor()
    for row in tablas:
        s, base, owner, obj, tipo, _, _, _, _, _, text = row
        objcompleto = base + "." + owner + "." + obj
        widgets[0] = FormatLabel('[{0}]'.format(objcompleto.ljust(80)[:80]))
        SQL = SQL_ddl.replace('{base}', base).replace('{objname}', obj).replace('{owner}', owner)
        cursorc.execute(SQL)
        text = cursorc.fetchone()
        new_row = (row[0], row[1], row[2], row[3], row[4], None, None, None, None, None,  text[0])
        resultados.append(new_row)
        i = i + 1
        bar.update(i)
    bar.finish()
    return resultados
