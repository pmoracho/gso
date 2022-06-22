try:
    import sys
    import gettext
    from gettext import gettext as _
    gettext.textdomain('migrador')

    from progressbar import ProgressBar
    from progressbar import FormatLabel
    from progressbar import Percentage
    from progressbar import Bar
    from progressbar import RotatingMarker
    from progressbar import ETA
    import time
    import os
    from cmdline.__version__  import NAME
    from cmdline.__version__  import DESCRIPTION
    from cmdline.__version__  import URL
    from cmdline.__version__  import AUTHOR
    from cmdline.__version__  import VERSION
    from cmdline.__version__  import EMAIL
    from cmdline.options import init_argparse
    from cmdline.log import Log
    from cmdline.config import Config

except ImportError as err:
    modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
    print(_("No fue posible importar el modulo: %s") % modulename)
    sys.exit(-1)

def sum_function_to_test(a, b):
    return a+b

title = """

  .oooooo.   ooo        ooooo oooooooooo.   ooooo        ooooo ooooo      ooo oooooooooooo
 d8P'  `Y8b  `88.       .888' `888'   `Y8b  `888'        `888' `888b.     `8' `888'     `8
888           888b     d'888   888      888  888          888   8 `88b.    8   888
888           8 Y88. .P  888   888      888  888          888   8   `88b.  8   888oooo8
888           8  `888'   888   888      888  888          888   8     `88b.8   888    "
`88b    ooo   8    Y     888   888     d88'  888       o  888   8       `888   888       o
 `Y8bood8P'  o8o        o888o o888bood8P'   o888ooooood8 o888o o8o        `8  o888ooooood8


{0} (v.{1})
by {2} <{3}>

"""

def main():

    args = init_argparse().parse_args()

    if args.commando not in ["test"]:

        exit(0)

    if not args.quiet:
        print(title.format(DESCRIPTION, VERSION, AUTHOR, EMAIL))

    log = Log(outputpath=args.logfile,
             loglevel=args.loglevel,
             quiet=args.quiet
    )

    log.info("Starting {0} - {1} (v{2})".format(NAME, DESCRIPTION, VERSION))
    try:
        cfgfile = os.path.join(os.getcwd(), 'cmdline.cfg')
        config = Config(cfgfile)
        log.info("Loading config: {}".format(cfgfile))

        f = 1
        t = config.progress_bar_ticks
        widgets = [FormatLabel(''), ' ', Percentage(), ' ', Bar('#'), ' ', ETA(), ' ', RotatingMarker()]
        bar = ProgressBar(widgets=widgets, maxval=t)

        for i in range(1, t+1):
            widgets[0] = FormatLabel('[Contador: {0}]'.format(i))
            time.sleep(.5)
            bar.update(i)

        bar.finish()
    except FileNotFoundError:
        errormsg = "No existe el archivo de configuración ({0})".format(cfgfile)
        print(errormsg)
        log.error(errormsg)
        sys.exit(-1)
