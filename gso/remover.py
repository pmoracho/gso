import pyodbc
import os
import glob
from pathlib import Path
from gso.tabulate import tabulate
from gso.objetos import get_objects, objetos_def
from gso.helper import  slugify

from progressbar import ProgressBar
from progressbar import FormatLabel
from progressbar import Percentage
from progressbar import Bar
from progressbar import RotatingMarker
from progressbar import ETA

def get_objetos_a_borar(cfg, object_pattern):

    objetos = get_objects(cfg, object_pattern)

    logicos = set()
    for server, database, owner, objname, tipo, modificado, mobject, text in objetos:
        logicos.add("|".join([database.lower(), (objetos_def[tipo]["folder"]).lower(), owner + '.' + objname]))

    databases = set(database.lower() for server, database, owner, objname, tipo, modificado, mobject, text in objetos)
    tipos = set(objetos_def[tipo]["folder"].lower() for server, database, owner, objname, tipo, modificado, mobject, text in objetos)
    objetos = set(objetos_def[tipo]["folder"].lower() for server, database, owner, objname, tipo, modificado, mobject, text in objetos)

    fisicos = set()
    for file in glob.iglob(cfg.export_path + '\\**\\*.sql', recursive=True):
        partes = file.replace(cfg.export_path + '\\', "").split("\\")
        #print(partes)
        if len(partes) == 3 and partes[0] not in ['Tools'] :
            db, tipo_objeto, objeto  = partes
            if ".sql" in objeto and db in databases and tipo_objeto in tipos:
                fisicos.add("|".join([db, tipo_objeto, objeto.replace(".sql", "")]))

    a_borrar = []
    for f in [fisico for fisico in fisicos if fisico not in logicos]:
        file = cfg.export_path + '\\' + f.replace('|', '\\') + '.sql'
        if os.path.isfile(file):
            a_borrar.append((file,))
        else:    ## Show an error ##
            print("Error: %s file not found" % file)

    return a_borrar


def show_remove_objects(a_borrar):

    print('Objetos eliminados de las bases de datos:')
    tablestr = tabulate(
                    tabular_data		= a_borrar,
                    headers				=  ['Archivo a borrar'],
                    tablefmt			= "psql",
                    stralign			= "left"
        )

    print(tablestr)
    print("Archivos eliminados: {0}".format(len(a_borrar)))

def test_remove(cfg, object_pattern):

    a_borrar = get_objetos_a_borar(cfg, object_pattern)
    show_remove_objects(a_borrar)

def remove(cfg, object_pattern):

    a_borrar = get_objetos_a_borar(cfg, object_pattern)
    for f in a_borrar:
        os.remove(f[0])

    show_remove_objects(a_borrar)