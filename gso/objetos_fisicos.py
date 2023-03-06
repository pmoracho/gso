import pyodbc
import os
import re
import fnmatch

from pathlib import Path
from gso.tabulate import tabulate
from gso.export_helpers import *
from gso.helper import slugify
from gso.export_helpers import was_modified_last_ndays

def search_folder(cwd, searchParam, searchResults, recursive=False):

    try:
        dirs = os.listdir(cwd)
    except FileNotFoundError:
        return

    for dir in dirs:
        fullpath = os.path.join(cwd,dir)
        if os.path.isdir(fullpath) and recursive:
            search_folder(fullpath, searchParam, searchResults, recursive)
        if re.search(searchParam,fullpath, re.IGNORECASE):
            searchResults.append(fullpath)


def get_phisical_objects(cfg, object_pattern, ndays=None):

    servers = []
    columns = []
    objetos = []

    # tipoObjetofisico.servidor.database
    tipo_objeto_fisico_solicitado, server_solicitado, base_solicitada = tuple(object_pattern.split('.'))

    tipo_objeto_fisico_solicitado = 'NULL' if tipo_objeto_fisico_solicitado == "*" else "'" + tipo_objeto_fisico_solicitado + "'"
    server_solicitado = 'NULL' if server_solicitado == "*" else "'" + server_solicitado + "'"
    base_solicitada = 'NULL' if base_solicitada == "*" else "'" + base_solicitada + "'"

    SQL = f"""
SET NOCOUNT OFF;

DECLARE @ErrorMessage	VARCHAR(MAX)
EXEC [g-track].dbo.[List_Phisical_Objects_Types]
		@Ambiente		    = 'desa',
		@TipoObjetoFisico	= {tipo_objeto_fisico_solicitado},
		@Servidor		    = {server_solicitado},
		@Database		    = {base_solicitada},
		@ErrorMessage		= @ErrorMessage OUTPUT

SELECT @ErrorMessage AS the_output;
""".format(tipo_objeto_fisico_solicitado, server_solicitado, base_solicitada)


    connectstr = cfg.servers[cfg.master_server]
    cnxn = pyodbc.connect(connectstr)
    cursor = cnxn.cursor()
    cursor.execute(SQL)
    tipos_objetos_fisicos = list(cursor.fetchall())
    cursor.close()

    objetos = []
    for row in tipos_objetos_fisicos:

        (ambiente, ambiente_descripcion, grupo, grupo_descripcion, db_datos, db_sistemas,
        servirdor, servidor_descripcion, cadena_conexion, tipo_objeto_fisico, patron_seleccion,
        path, flag_recursivo) = row

        searchResults = [];
        recursive = True if flag_recursivo == 1 else False

        search_folder(path, patron_seleccion, searchResults, recursive)
        for file in searchResults:

            dirname =  os.path.dirname(file.replace(path, ""))
            dstpath = os.path.join(cfg.export_path, db_sistemas, tipo_objeto_fisico, dirname).lower()
            dstfile = os.path.join(dstpath, slugify(os.path.basename(file)))

            if ndays is None or was_modified_last_ndays(file, int(ndays)):
                objetos.append(
                    (db_sistemas, tipo_objeto_fisico, os.path.join(path, file), dstfile)
                )


    return objetos


def get_parts_from_object_pattern(object_pattern):
    return tuple(object_pattern.split('.'))