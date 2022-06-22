import logging
import os

class Log:

    def __init__(self, outputpath, loglevel, quiet = True):

        logging.basicConfig(filename=os.path.join(outputpath, 'cmdline.log'),
                            level=getattr(logging, loglevel.upper(), None),
                            format='%(asctime)s|%(levelname)s|%(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S',
                            filemode='w')
        self.quiet = quiet


    def info(self, msg):

        if not self.quiet:
            print(msg)

        logging.info(msg.replace("|", " "))

    def error(self, msg):
        msg = "!!! Error ---> {0}".format(msg.replace("|", " "))
        if not self.quiet:
            print(msg)

        logging.error("Error: {0}".format(msg))
