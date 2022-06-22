try:
    import sys
    import gettext
    from gettext import gettext as _
    gettext.textdomain('gso')

    from progressbar import ProgressBar
    from progressbar import FormatLabel
    from progressbar import Percentage
    from progressbar import Bar
    from progressbar import RotatingMarker
    from progressbar import ETA
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
        config = Config(cfgfile)
        log.info("Loading config: {}".format(cfgfile))

        # f = 1
        # t = config.progress_bar_ticks
        # widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]
        # bar = ProgressBar(widgets=widgets, maxval=t)

        # for i in range(1, t+1):
        #     widgets[0] = FormatLabel('[Contador: {0}]'.format(i))
        #     time.sleep(.5)
        #     bar.update(i)

        # bar.finish()

        export(config, args.objeto)

    except FileNotFoundError:
        errormsg = "No existe el archivo de configuración ({0})".format(cfgfile)
        print(errormsg)
        log.error(errormsg)
        sys.exit(-1)
