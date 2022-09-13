import glob
import re
import collections
import csv

url_root = "https://github.com/Marval-O-Farrell-Mairal/Mecanus-apps-concept/blob/main"
repo_path = "D:\\PM\\repos\\Mecanus-apps-concept"
patrones = {
    "Contable_db": {
        # STRING->Contable_db
        "STRING": [r"(Contable_db)\."],
        # OBJETO
        "OBJETO": [r"Contable_db\.\w*\.(?P<OBJETO>\w+)\s"],
        # SP->Nombre del Sp
        "SP": [
            r"EXEC.*Contable_db\.\w*\.(?P<SP>\w+)"
            ],
        # TABLA->Modo de uso y Nombre de tabla
        # Con y sin linked server
        "TABLA": [
            r"(FROM|JOIN|DELETE|INSERT\sINTO|UPDATE)\sContable_db\.\w*\.(?P<TABLA>\w+)",
            r"(FROM|JOIN|DELETE|INSERT\sINTO|UPDATE)\s\w+\.Contable_db\.\w*\.(?P<TABLA>\w+)"
        ],
        # FUNCION->Nombre de la funcion
        "FUNCION": [
            r"SELECT.*Contable_db\.\w*\.(?P<FUNCION>\w+)\s\("
        ]
    }
}

def process(file):

    resultados = []
    partes = file.replace(repo_path + '\\', "").split("\\")
    if len(partes) != 3:
        return

    db, tipo_objeto, objeto  = partes
    url = url_root + "/" + db + "/" + tipo_objeto + "/" + objeto
    objeto =  objeto.replace('.sql', '')
    with open(file, 'r', encoding="utf8") as fp:
        data = fp.read().rstrip()

        for patron, tipos in patrones.items():
            for tipo, regexes in tipos.items():
                for regex in regexes:
                    matches = re.finditer(regex, data, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for matchNum, match in enumerate(matches, start=1):
                        cant_grupos = len(match.groups())
                        if cant_grupos == 1:
                            modo = ""
                            destino = match.groups(1)[0]
                        else:
                            modo = match.groups(1)[0]
                            destino = match.groups(2)[1]

                        destino = destino.lower() if tipo in "STRING" else destino
                        resultados.append((patron, url, db, tipo_objeto, objeto, tipo, modo, destino))

    counter = collections.Counter(resultados)
    resultados = [(k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7], v) for k, v in collections.Counter(resultados).items()]
    return resultados



with open('export.csv', mode='wt', newline='') as out:
    csv_out = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_out.writerow(["patrón", "url", "Db", "Obj", "Nombre", "Conexión", "Modo", "A", 'Cant'])
    for file in glob.iglob(repo_path + '\\**\\*.sql', recursive=True):
        try:
            resultados = process(file)
        except UnicodeDecodeError as e:
            print("Error de decodificación en {f}: {e}".format(f=file, e=e))
        if resultados:
            csv_out.writerows(resultados)
