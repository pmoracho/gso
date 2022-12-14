import gettext
from gettext import gettext as _

gettext.textdomain('gso')

from gso.__version__  import NAME
from gso.__version__  import DESCRIPTION
from gso.__version__  import URL
from gso.__version__  import AUTHOR
from gso.__version__  import VERSION
from gso.__version__  import TITLE

def _my_gettext(s):
    """Traducir algunas cadenas de argparse."""
    current_dict = {'usage: ': 'uso: ',
                    'optional arguments': 'argumentos opcionales',
                    'show this help message and exit': 'mostrar esta ayuda y salir',
                    'positional arguments': 'argumentos posicionales',
                    'the following arguments are required: %s': 'los siguientes argumentos son requeridos: %s'}

    if s in current_dict:
        return current_dict[s]
    return s

gettext.gettext = _my_gettext

import argparse


def init_argparse():
    """Inicializar parametros del programa."""

    epilog =  """

Patrón de selección:
    <tipo de objeto>.<conexión>.<database>.<owner>.<nombre del objeto>

Tipos de objeto a seleccionar:
    P : Stored procedure
    PV: Stroed procdure (versionado)
    FN: SQL scalar function
    IF: SQL inline table-valued function
    TF: SQL table-valued-function
    FN: Funcion
    IF: Escalr function
    FF: Todas las funciones
    TR: Trigger
    D : Default
    R : Rule
    OP: Operacón
    PR: Parametro
    PA: Procesos Agenda
    TT: Tabla temporal mecanus
    TB: Tabla física de SQL Server
    MO: Modulos
    ME: Menú de sistema
    RP: Reporte

Ejemplos:\n

Para exportar todos los objetos a un carpeta físicasegún se define en archivo.cfg:
   gso export  *.*.*.*.* --config archivo.cfg

Para exportar todos los objetos de una determinada conexión:
   gso export  *.momdesa1.*.*.* --config archivo.cfg

 Para exportar todos las tablas físicas de cierta base/owner con cierto patron:
   gso export  TB.momdesa1.contable_db.dbo.MAC --config archivo.cfg
"""

    cmdparser = argparse.ArgumentParser(prog=NAME,
                                        description=TITLE,
                                        epilog=epilog,
                                        add_help=True,
                                        formatter_class=make_wide(argparse.RawTextHelpFormatter, w=80, h=48)
    )

    opciones = {    "verbo": {
                                "help": _("Accion a ejecutar")
                    },
                    "patron": {
                                "help": _("Patron del objeto a exportar")
                    },
                    "--version -v": {
                                "action":    "version",
                                "version":    VERSION,
                                "help":        _("Mostrar el número de versión y salir")
                    },
                    "--log-level -n": {
                                "type":     str,
                                "action":   "store",
                                "dest":     "loglevel",
                                "default":  "info",
                                "help":     _("Nivel de log")
                    },
                    "--log-file -l": {
                            "type":	str,
                            "action": "store",
                            "dest":	"logfile",
                            "default": "",
                            "help":	_("Archivo de log"),
                            "metavar": "file"
                    },
                    "--config-file -c": {
                            "type":	str,
                            "action": "store",
                            "dest":	"config_file",
                            "default": "gso.cfg",
                            "help":	_("Archivo de configuración"),
                            "metavar": "file"
                    },
                    "--quiet -q": {
                                "action":     "store_true",
                                "dest":     "quiet",
                                "default":    False,
                                "help":        _("Modo silencioso sin mostrar absolutamente nada.")
                    },
                    "--last-n-days -d": {
                            "type":	int,
                            "action": "store",
                            "dest":	"ndays",
                            "default": None,
                            "help":	_("Configura la cantidad de días de los objetos modificados a recuperar"),
                            "metavar": "dias"
                    },
            }

    for key, val in opciones.items():
        args = key.split()
        kwargs = {}
        kwargs.update(val)
        cmdparser.add_argument(*args, **kwargs)

    return cmdparser

def make_wide(formatter, w=120, h=40):
    """Return a wider HelpFormatter, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {'width': w, 'max_help_position': h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("argparse help formatter failed, falling back.")
        return formatter