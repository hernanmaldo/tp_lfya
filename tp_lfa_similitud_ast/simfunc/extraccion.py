"""Extracción: recorre un directorio, parsea cada .py y obtiene sus funciones."""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

TIPOS_FUNCION = (ast.FunctionDef, ast.AsyncFunctionDef)
DIRS_IGNORADOS = {".git", "__pycache__", ".venv", "venv", "env", ".tox", "node_modules"}


@dataclass
class Funcion:
    """Una función extraída del repositorio."""
    nombre: str          # nombre original (no participa de la comparación)
    archivo: str         # ruta relativa al directorio analizado
    linea: int           # línea de la definición
    nodo: ast.AST = field(repr=False)  # subárbol AST original
    tokens: list[str] = field(default_factory=list, repr=False)  # se completa luego

    @property
    def id(self) -> str:
        return f"{self.archivo}:{self.nombre}:{self.linea}"


def extraer_de_codigo(codigo: str, archivo: str = "<codigo>") -> list[Funcion]:
    """Parsea código fuente y devuelve TODAS las funciones (incluidas métodos y anidadas)."""
    arbol = ast.parse(codigo, filename=archivo)
    return [
        Funcion(nombre=n.name, archivo=archivo, linea=n.lineno, nodo=n)
        for n in ast.walk(arbol)
        if isinstance(n, TIPOS_FUNCION)
    ]


def iterar_archivos_py(directorio: str | Path):
    """Recorre recursivamente el directorio devolviendo los .py (orden determinístico)."""
    raiz = Path(directorio)
    for ruta in sorted(raiz.rglob("*.py")):
        if any(parte in DIRS_IGNORADOS for parte in ruta.relative_to(raiz).parts):
            continue
        yield ruta


def extraer_de_directorio(directorio: str | Path, verbose: bool = False) -> list[Funcion]:
    """Extrae las funciones de todos los .py del directorio.

    Los archivos con errores de sintaxis o de codificación se omiten (con aviso si verbose).
    """
    raiz = Path(directorio)
    funciones: list[Funcion] = []
    for ruta in iterar_archivos_py(raiz):
        rel = ruta.relative_to(raiz).as_posix()
        try:
            codigo = ruta.read_text(encoding="utf-8")
            funciones.extend(extraer_de_codigo(codigo, rel))
        except (SyntaxError, UnicodeDecodeError, ValueError) as e:
            if verbose:
                print(f"[aviso] se omite {rel}: {e}")
    return funciones
