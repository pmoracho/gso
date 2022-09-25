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

todo = """To do:
1. Recoremos las carpeta del repositorio de forma recursiva
2. Por cada pat completo al archivo
    * obtenemos, database, tipo de objeto, owner, nombre del objeto
    * Por cada database
        * Nos conectamos
        * Verificamos si existe el objeto
        * Si no existe en ninguno eliminamos el archivo
"""

def remove(cfg):

    for file in glob.iglob(repo_path + '\\**\\*.sql', recursive=True):
        partes = file.replace(repo_path + '\\', "").split("\\")
        if len(partes) == 3:
            db, tipo_objeto, objeto  = partes