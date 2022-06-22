# cmdline

__A simple command line script template for new proyects__

Un simple template o modelo de un script de linea de comando para usar en la
construcción de cualquier nueva herramienta de este tipo.

### características

* Simple y estándar
* Uso de `setup.py`
* `progressbar2` como ejemplo de requerimiento externo y además por que resulta útil
* `pytest` para manejar las pruebas unitarias
* Congfiguración tipo `INI`
* Log con `logging`
* `docker`izable


# Instalación y desarrollo
## Requerimientos básicos:

Tener instalado y funcionando:

* [Git][git]
* [Python 3.x][python]

## Entorno inicial básico

El primer paso es descargar el repositorio y preparar el entorno inicial que
servirá tanto sea para desarrollo como para eventual ejecución de la
herramienta.

* Clonar repositorio
* Crear entorno virtual
* Activar entorno virtual
* actualizar `pip` y `setuptool`
* Instalar requerimientos
* Instalar `pytest`

```
git clone https://github.com/pmoracho/cmdline.git
cd cmdline
python -m venv .venv --prompt=cmdline

# En Windows
.venv\Scripts\activate.bat

# En Linux
source .venv/bin/activate

# Actualizar pip y setuptools
python -m pip install --upgrade pip
pip install --upgrade setuptools

# Instalar  paquetes requeridos
pip install -r requirements.txt
```

Finalmente, luego de los pasos anteriores, con el entorno activo podemos hacer:

```
python setup.py develop
```

Esto genera un script de ejecución consistente entre plataformas que en el caso
de este template se llamará `cmdline`. El código del mismo:

```python
#!<root path>/cmdline/.venv/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'cmdline','console_scripts','cmdline'
import re
import sys

# for compatibility with easy_install; see #2198
__requires__ = 'cmdline'

try:
    from importlib.metadata import distribution
except ImportError:
    try:
        from importlib_metadata import distribution
    except ImportError:
        from pkg_resources import load_entry_point


def importlib_load_entry_point(spec, group, name):
    dist_name, _, _ = spec.partition('==')
```

Con esto logramos que sea posible ejecutar `cmdline` desde `<root
path>/cmdline/.venv/bin/python`, dónde `<root path>` será la carpeta base en
dónde hemos instalado este proyecto, la ejecución usará el interprete `python`
del entorno virtual, algo fundamental ya que es en este entorno dónde hemos
instalado los requerimientos de la herramienta.

### Testing

Este proyecto implementa una carpeta `test` con una prueba muy simple de una
función del módulo `core.py`, las pruebas se ejecutan mediante `pytest`, el cual
se deberá instalar si se elije seguir usando este procedimiento:

```
pip install pytest
```

Luego, para ejecutar los tests:

```
pytest
```



## Comenzando un nuevo proyecto

Una vez completada la instalación inicial, los primeros cambios para crear un
nuevo proyecto a partir de este template serían:

1. Modificar `setup.py`:
    * Datos de la herramienta: `NAME`, `DESCRIPTION`, `URL`, `EMAIL`, `AUTHOR`
    * Paquetes requeridos `REQUIRED`
    * Clasificadores para **PyPy**: `setup(..., classifiers)`
    * `entry_points`, según sea la invocación del código principal del script.
2. Configuración de versión en `cmdline/__version__.py`
3. Editar código en `cmdline/core.py`
4. Renombrar proyecto y carpeta del módulo `cmdline` por el nombre de la nueva herramienta
5. Eliminar repositorio `.git` y generar una nuevo con `git init`


[git]: https://git-scm.com/
[python]: https://www.python.org/
