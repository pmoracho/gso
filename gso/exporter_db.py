import pyodbc
import os
from pathlib import Path
from gso.tabulate import tabulate
from gso.export_helpers import *
from gso.helper import slugify
from gso.objetos_logicos import *
from progressbar import ProgressBar
from progressbar import FormatLabel
from progressbar import Percentage
from progressbar import Bar
from progressbar import RotatingMarker
from progressbar import ETA

def test_export_db(cfg, object_pattern, ndays=None):

    print("Creating list of objects (Tables/Code/Mecanus Objects)")
    objetos = get_logical_objects(cfg, object_pattern, ndays)


    tablestr = tabulate(
                    tabular_data		= [row[:-1] for row in objetos],
                    headers				=  ['server', 'db', 'owner', 'objeto', 'tipo', 'modificado', 'mecanus'],
                    tablefmt			= "psql",
                    stralign			= "left"
        )

    print(tablestr)
    print("{0} objetos".format(len(objetos)))

def export_db(cfg, object_pattern, ndays=None):

    print("Creating list of objects (Tables/Code/Mecanus Objects)")
    objetos = get_logical_objects(cfg, object_pattern, ndays)

    print("Exporting objects to files")
    i = 0
    t = len(objetos)

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]
    bar = ProgressBar(widgets=widgets, maxval=t)

    for server, database, owner, objname, tipo, modificado, mobject, text in objetos:

        widgets[0] = FormatLabel('[W: {0}.{1}.{2}.{3}]'.format(server, database, tipo, objname))

        path = os.path.join(cfg.export_path, database, objetos_def[tipo]["folder"]).lower()
        file = objetos_def[tipo]["name_format"].replace("{owner}", owner).replace("{objname}", objname)
        file = os.path.join(path, slugify(file) + '.sql')

        if text:
            p = Path(path)
            p.mkdir(parents=True, exist_ok=True)
            objetos_def[tipo]["export"](database, owner, objname, path, file, text)

        i = i + 1
        bar.update(i)
    bar.finish()

