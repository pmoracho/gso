import pyodbc
import os
import glob
from pathlib import Path
from gso.tabulate import tabulate
from gso.exporter import get_objects, objetos_def
from gso.helper import  slugify

from progressbar import ProgressBar
from progressbar import FormatLabel
from progressbar import Percentage
from progressbar import Bar
from progressbar import RotatingMarker
from progressbar import ETA


def remove(cfg, object_pattern):

    objetos = get_objects(cfg, object_pattern)

    logicos = set()
    for _, base, owner, obj, tipo, _, _, _, _, _, _ in objetos:
        logicos.add("|".join([base.lower(), (objetos_def[tipo]["folder"]).lower(), owner + '.' + obj]))

    fisicos = set()
    for file in glob.iglob(cfg.export_path + '\\**\\*.sql', recursive=True):
        partes = file.replace(cfg.export_path + '\\', "").split("\\")
        if len(partes) == 3 and partes[0] not in ['Tools']:
            db, tipo_objeto, objeto  = partes
            if ".sql" in objeto:
                fisicos.add("|".join([db, tipo_objeto, objeto.replace(".sql", "")]))

    # print(next(iter(logicos)))
    # print("----------------")
    # print(next(iter(fisicos)))
    # print(fisicos.difference(logicos))

    print('Objetos eliminados de las bases de datos:')
    total = 1
    for f in [fisico for fisico in fisicos if fisico not in (logicos)]:
        file = cfg.export_path + '\\' + f.replace('|', '\\') + '.sql'
        if os.path.isfile(file):
            # print(file)
            os.remove(file)
            total = total + 1
        else:    ## Show an error ##
            print("Error: %s file not found" % file)

    print("Archivos eliminados: {0}".format(total))