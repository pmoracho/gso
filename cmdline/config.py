from configparser import ConfigParser
from pydoc import locate

class Config:

    DEF_CFG = {"lista_cadenas": ["jpg"],
               "lista_enteros": [20, 20, 20, 20],
               "float": 1.0,
               "entero": 150,
               "booleano": False,
               "cadena": '',
               "progress_bar_ticks": 20,
            }

    def __init__(self, file=None, override_section=None):

        self.config = ConfigParser()
        self.__dict__.update(self.DEF_CFG)

        self.file = file
        self.override_section = override_section

        if self.file:
            if isinstance(self.file, str):
              self.file = open(self.file, "rt")

            self._load('Config')
            if self.override_section:
                  self._load(self.override_section)

    def _load(self, section):

        self.config.read_file(self.file)
        items_ini = self.config.items(section)

        for (k, v) in items_ini:

          if k in self.__dict__:
            d = self.__dict__[k]
            if isinstance(d, list):
                first = d[0]
                self.__dict__[k] = list(map(locate(type(first).__name__),
                                            [x.strip() for x in v.split(',')]))
            else:
                self.__dict__[k] = locate(type(d).__name__)(v)

    def __str__(self):

      return f"""
-------------- Config -------------------
lista_cadenas: {self.lista_cadenas}
lista_enteros: {self.lista_enteros}
        float: {self.float}
       entero: {self.entero}
     booleano: {self.booleano}
       cadena: {self.cadena}
-----------------------------------------
      """
