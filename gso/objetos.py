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

objetos_def = {
    "P": {"folder": "sp", "export": export_sp, "name_format": "{owner}.{objname}"},
    "PV": {"folder": "spv", "export": export_sp, "name_format": "{owner}.{objname}"},
    "V": {"folder": "view", "export": export_content, "name_format": "{owner}.{objname}"},
    "FN": {"folder": "fn", "export": export_function, "name_format": "{owner}.{objname}"},
    "IF": {"folder": "fn", "export": export_function, "name_format": "{owner}.{objname}"},
    "TR": {"folder": "trg", "export": export_content, "name_format": "{owner}.{objname}"},
    "R": {"folder": "rule", "export": export_content, "name_format": "{owner}.{objname}"},
    "TF": {"folder": "fn", "export": export_function, "name_format": "{owner}.{objname}"},
    "D": {"folder": "dft", "export": export_content, "name_format": "{owner}.{objname}"},
    "TB": {"folder": "tbl", "export": export_table, "name_format": "{owner}.{objname}"},
    "TT": {"folder": "mobj\\tblt", "export": export_content, "name_format": "{objname}"},
    "RP": {"folder": "mobj\\rpt", "export": export_content, "name_format": "{objname}"},
    "PR": {"folder": "mobj\\pmt", "export": export_content, "name_format": "{objname}"},
    "PA": {"folder": "mobj\\pa", "export": export_content, "name_format": "{objname}"},
    "MO": {"folder": "mobj\\mo", "export": export_content, "name_format": "{objname}"},
    "OP": {"folder": "mobj\\op", "export": export_content, "name_format": "{objname}"},
    "ME": {"folder": "mobj\\menu", "export": export_content, "name_format": "{objname}"},
}

type_obj = {v["folder"]: k for k, v in objetos_def.items()}


def get_object_text(cnxn, server, database, owner, objname, tipo_objeto):

    SQL_ddl = """
SET NOCOUNT ON
DECLARE @Script		   NVARCHAR(MAX)
DECLARE @ErrorMessage  VARCHAR(2000)

EXEC [g-track].dbo.Export_Mecanus_Object
		@Database	    = '{database}',
        @TipoObjeto     = '{tipo_objeto}',
        @Owner          = '{owner}',
		@ObjectId	    = '{objname}',
        @FlagGIT	    = 1,
        @FlagOnlyScript	= 1,
        @FilePath       = NULL,
		@Script		    = @Script OUTPUT,
		@ErrorMessage   = @ErrorMessage OUTPUT;

SET NOCOUNT OFF
SELECT @Script
"""
    cursorc = cnxn.cursor()
    SQL = SQL_ddl.replace('{database}', database).replace('{objname}', objname).replace('{tipo_objeto}', tipo_objeto).replace('{owner}', owner)
    # print(SQL)
    cursorc.execute(SQL)
    text = cursorc.fetchone()
    return text

SQL_Objetos = """

SET NOCOUNT OFF;

DECLARE @ErrorMessage	VARCHAR(MAX)
EXEC [g-track].dbo.[List_Objects]
        @Database       = '{database}',
        @DaysFromChange = {ndays},
        @Owner          = '{owner_solicitado}',
        @ObjectName     = '{objname_solicitado}',
        @ObjectType     = '{objec_type_solicitado}',
        @ErrorMessage   = @ErrorMessage OUTPUT;

SELECT @ErrorMessage AS the_output;
"""


def get_objects(cfg, object_pattern, ndays=None):

    servers = []
    columns = []
    objetos = []

    objec_type_solicitado, server_solicitado, base_solicitada, owner_solicitado, objname_solicitado = get_parts_from_object_pattern(object_pattern)

    if server_solicitado == '*':
        servers = list(cfg.servers)
    else:
        servers.append(server_solicitado)

    objname_solicitado = '' if objname_solicitado == '*' else objname_solicitado
    owner_solicitado = '' if owner_solicitado == '*' else owner_solicitado
    objec_type_solicitado = '' if objec_type_solicitado == '*' else objec_type_solicitado
    ndays = ndays if ndays else 'NULL'

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


        for database in bases:

            SQL = SQL_Objetos.replace('{database}', database).replace('{ndays}', ndays).replace('{owner_solicitado}', owner_solicitado).replace('{objname_solicitado}', objname_solicitado).replace('{objec_type_solicitado}', objec_type_solicitado)
            # print(SQL)
            cursorb = cnxn.cursor()
            cursorb.execute(SQL)
            rows = cursorb.fetchall()
            cnxn.commit()

            if rows:

                i = 0
                t = len(rows)

                widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]
                bar = ProgressBar(widgets=widgets, maxval=t)

                resultados = []
                for row in rows:
                    if not row[7]:
                        text = get_object_text(cnxn, server, database, row[2], row[3], row[4])
                        row[7] = text[0]

                    widgets[0] = FormatLabel('[R: {0}.{1}.{2}.{3}]'.format(server, database, row[4], row[3]))
                    objetos.extend((row,))
                    i = i + 1
                    bar.update(i)

                bar.finish()

            cursorb.close()


    return objetos


def get_parts_from_object_pattern(object_pattern):
    return tuple(object_pattern.split('.'))

