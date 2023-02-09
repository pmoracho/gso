import pyodbc
import os
import shutil
from pathlib import Path
from gso.tabulate import tabulate
from gso.export_helpers import *
from gso.helper import slugify
from gso.objetos_fisicos import *
from progressbar import ProgressBar
from progressbar import FormatLabel
from progressbar import Percentage
from progressbar import Bar
from progressbar import RotatingMarker
from progressbar import ETA

def test_export_fisicos(cfg, object_pattern, ndays=None):

    print("Creating list of phisical objects")
    objetos = get_phisical_objects(cfg, object_pattern, ndays)


    tablestr = tabulate(
                    tabular_data		= [row for row in objetos],
                    headers				=  ['db', 'tipo objeto', 'file', 'file (dst)'],
                    tablefmt			= "psql",
                    stralign			= "left"
        )

    print(tablestr)
    print("{0} objetos".format(len(objetos)))

def export_fisicos(cfg, object_pattern, ndays=None):

    print("Creating list of phisical objects")
    objetos = get_phisical_objects(cfg, object_pattern, ndays)

    print("Exporting objects to files")
    i = 0
    t = len(objetos)

    widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]
    bar = ProgressBar(widgets=widgets, maxval=t)

    for database, tipo_objeto, file, dstfile in objetos:

        widgets[0] = FormatLabel('[W: {0}.{1}.{2}]'.format(database, tipo_objeto, file))

        p = Path(os.path.dirname(dstfile))
        try:
            p.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        shutil.copyfile(file, dstfile, )

        i = i + 1
        bar.update(i)

    bar.finish()

