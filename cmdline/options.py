import gettext
from gettext import gettext as _

gettext.textdomain('cmdline')

from cmdline.__version__  import NAME
from cmdline.__version__  import DESCRIPTION
from cmdline.__version__  import URL
from cmdline.__version__  import AUTHOR
from cmdline.__version__  import VERSION

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
    cmdparser = argparse.ArgumentParser(prog=NAME,
                                        description="%s\n%s\n" % (DESCRIPTION, AUTHOR),
                                        epilog="",
                                        add_help=True,
                                        formatter_class=make_wide(argparse.HelpFormatter, w=80, h=48)
    )

    opciones = {    "commando": {
                                "help": _("Comando del migrador, export o import")
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
                    "--quiet -q": {
                                "action":     "store_true",
                                "dest":     "quiet",
                                "default":    False,
                                "help":        _("Modo silencioso sin mostrar absolutamente nada.")
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