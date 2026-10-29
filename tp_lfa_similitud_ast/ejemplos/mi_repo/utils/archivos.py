import json
import os


def leer_json(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta)
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, indent=2)


class Cache:
    def __init__(self):
        self.datos = {}

    def obtener(self, clave, por_defecto=None):
        try:
            return self.datos[clave]
        except KeyError:
            return por_defecto

    async def refrescar(self, cargador):
        self.datos = await cargador()
        return len(self.datos)
