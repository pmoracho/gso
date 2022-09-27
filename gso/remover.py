import pyodbc
import os
import glob
from pathlib import Path
from gso.tabulate import tabulate
from gso.exporter import get_objects, obj_type

from progressbar import ProgressBar
from progressbar import FormatLabel
from progressbar import Percentage
from progressbar import Bar
from progressbar import RotatingMarker
from progressbar import ETA

def remove(cfg):

    objetos = get_objects(cfg, "*.*.*.*.*")

    logicos = set()
    for _, base, owner, obj, tipo, _, _, _, _, _, _ in objetos:
        logicos.add(".".join([base.lower(), (obj_type[tipo]).lower(), owner, obj]))

    fisicos = set()
    for file in glob.iglob(cfg.export_path + '\\**\\*.sql', recursive=True):
        partes = file.replace(cfg.export_path + '\\', "").split("\\")
        if len(partes) == 3 :
            db, tipo_objeto, objeto  = partes
            if ".sql" in objeto:
                fisicos.add(".".join([db, tipo_objeto, objeto.replace(".sql", "")]))

    print('Objetos eliminados de las bases de daatos:')
    print(fisicos.difference(logicos))