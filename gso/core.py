try:
    import sys
    import time
    import gettext
    from gettext import gettext as _
    gettext.textdomain('gso')

    import time
    import os
    from gso.__version__  import NAME
    from gso.__version__  import DESCRIPTION
    from gso.__version__  import URL
    from gso.__version__  import AUTHOR
    from gso.__version__  import VERSION
    from gso.__version__  import EMAIL
    from gso.options import init_argparse
    from gso.log import Log
    from gso.config import Config
    from gso.exporter import export
    from gso.remover import remove

except ImportError as err:
    modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
    print(_("No fue posible importar el modulo: %s") % modulename)
    sys.exit(-1)

def sum_function_to_test(a, b):
    return a+b

title = """

 ██████╗ ███████╗ ██████╗
██╔════╝ ██╔════╝██╔═══██╗
██║  ███╗███████╗██║   ██║
██║   ██║╚════██║██║   ██║
╚██████╔╝███████║╚██████╔╝
 ╚═════╝ ╚══════╝ ╚═════╝

{0} (v.{1})
by {2} <{3}>

"""

def main():

    args = init_argparse().parse_args()

    if not args.objeto:
        exit(0)

    if not args.quiet:
        print(title.format(DESCRIPTION, VERSION, AUTHOR, EMAIL))

    log = Log(outputpath=args.logfile,
             loglevel=args.loglevel,
             quiet=args.quiet
    )

    log.info("Starting {0} - {1} (v{2})".format(NAME, DESCRIPTION, VERSION))
    try:
        cfgfile = os.path.join(os.getcwd(), args.config_file)
    except FileNotFoundError:
        errormsg = "No existe el archivo de configuración ({0})".format(cfgfile)
        print(errormsg)
        log.error(errormsg)
        sys.exit(-1)

    config = Config(cfgfile)
    log.info("Loading config: {}".format(cfgfile))

    start = time.time()
    if args.verbo == "export":
        export(config, args.objeto, args.ndays)

    if args.verbo == "remove":
        remove(config, "*.*.*.*.*")

    end = time.time()
    print("Tiempo de proceso: {0} minutos".format( (end - start)/60 ))


