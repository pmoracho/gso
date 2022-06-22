import os, tempfile, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cmdline.config import Config

def test_config():

    # Convert text into tmp file
    tmp_file = tempfile.NamedTemporaryFile(suffix=".cfg", delete=False)
    s_config = """
[Config]
booleano = "True"
lista_cadenas = jpg, png, tif
lista_enteros = 1, 2, 3
float = 100.90
entero = 2
cadena = epa
otracosa = 1
"""
    with open(tmp_file.name, "w") as f:
        f.write(s_config)
    c = Config(tmp_file.name)


    assert c.booleano == True
    assert c.float == 100.9
    assert c.lista_cadenas == ['jpg', 'png', 'tif']
    assert c.lista_enteros == [1, 2, 3]
    assert c.entero == 2
    assert c.cadena == "epa"
