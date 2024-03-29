# gso

__Get SQL & Mecanus objects__

Una herramienta de línea de comandos para:

* Extraer objetos de servidores de SQL SERVER y sal|varlos a un archivo.
* Copiar archivos físicos de los sistemas **Mecanus**, por ejemplo: reportes crystal

El sentido es el de poder migrar el desarrollo de las aplicaciones **Mecanus** a un
flujo de trabajo basado en `git`.

## Importante

La configuración y funcionalidad se basa en la base de datos `[g-track]`, debiera
haber una por motor y una versión "master" dónde reside la configuración.

## características

* Simple y estándar
* Uso de `setup.py`
* `progressbar2` como ejemplo de requerimiento externo y además por que resulta útil
* `pytest` para manejar las pruebas unitarias
* Congfiguración tipo `INI`
* Log con `logging`
* `docker`izable

## Objetos exportables

* Tablas físicas
    - Script de creación con índices
    - Datos
* Stored procedures
* Funciones
* Triggers
* Vistas

Adicionalmente:

* Objetos Mecanus
    - Operaciones
    - Parametros
    - Reportes
    - Modulos
    - Tablas temporales
    - Procesos agenda
    - Menu

* Archivos físicos
    - Reportes
    - Scripts

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
git clone https://github.com/pmoracho/gso.git
cd gso
python -m venv .venv --prompt=gso

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
de este template se llamará `gso`. El código del mismo:

```python
#!<root path>/gso/.venv/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'gso','console_scripts','gso'
import re
import sys

# for compatibility with easy_install; see #2198
__requires__ = 'gso'

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

Con esto logramos que sea posible ejecutar `gso` desde `<root
path>/gso/.venv/bin/python`, dónde `<root path>` será la carpeta base en
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



## Ejecutar `gso`

Configurar un archivo `.cfg` por ejemplo:

    [Config]
    progress_bar_ticks=20
    export_path = <path_al_repositorio>
    deploy_path= D:\tmp

    [Servers]
    server1 = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server1;DATABASE=master;UID=user;PWD=passwd;"
    server2 = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server2;DATABASE=master;UID=user;PWD=passwd;"

Ejecutar sobre todos lo servidores, bases, tipo de objetos y objetos:

    gso export_db *.*.*.*.* --config archivo.cfg

Para eliminar (objetos de la base que fueron "dropeados")

    gso remove_db *.*.*.*.* --config archivo.cfg

Para copiar objetos físcos:

    gso exportfiles *.*.sistemas_correspondencia --config archivo.cfg


[git]: https://git-scm.com/
[python]: https://www.python.org/
