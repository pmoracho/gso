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
    from gso.__version__  import TITLE
    from gso.options import init_argparse
    from gso.log import Log
    from gso.config import Config
    from gso.exporter_db import export_db
    from gso.exporter_db import test_export_db
    from gso.exporter_fisico import test_export_fisicos
    from gso.exporter_fisico import export_fisicos
    from gso.remover_db import remove_db
    from gso.remover_db import test_remove_db

except ImportError as err:
    modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
    print(_("No fue posible importar el modulo: %s") % modulename)
    sys.exit(-1)

def main():

    args = init_argparse().parse_args()

    if not args.verbo and not args.patron:
        exit(0)

    if not args.quiet:
        print(TITLE)

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

    if args.verbo == "test-exportdb":
        test_export_db(config, args.patron, args.ndays)

    if args.verbo == "exportdb":
        export_db(config, args.patron, args.ndays)

    if args.verbo == "removedb":
        remove_db(config, "*.*.*.*.*")

    if args.verbo == "test-removedb":
        test_remove_db(config, args.patron)

    if args.verbo == "test-exportfiles":
        test_export_fisicos(config, args.patron, args.ndays)

    if args.verbo == "exportfiles":
        export_fisicos(config, args.patron, args.ndays)

    end = time.time()
    print("Tiempo de proceso: {0} minutos".format( (end - start)/60 ))


