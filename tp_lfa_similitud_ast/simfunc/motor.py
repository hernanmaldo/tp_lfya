"""Motor de búsqueda: indexa un repositorio y devuelve las funciones más similares."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from .extraccion import Funcion, extraer_de_codigo, extraer_de_directorio
from .normalizacion import tokens_de_funcion
from .similitud import N_POR_DEFECTO, UMBRALES, similitud


@dataclass
class Resultado:
    funcion: Funcion
    score: float
    candidata: bool  # score >= umbral


class Motor:
    def __init__(self, directorio: str | Path, metrica: str = "jaccard",
                 n: int = N_POR_DEFECTO, umbral: float | None = None,
                 min_tokens: int = 0, verbose: bool = False):
        self.directorio = Path(directorio)
        if metrica not in UMBRALES:
            raise ValueError(f"métrica desconocida: {metrica!r}")
        self.metrica, self.n, self.min_tokens = metrica, n, min_tokens
        self.umbral = UMBRALES[metrica] if umbral is None else umbral
        self.funciones = extraer_de_directorio(self.directorio, verbose=verbose)
        for f in self.funciones:
            f.tokens = tokens_de_funcion(f.nodo)
        if min_tokens:
            self.funciones = [f for f in self.funciones if len(f.tokens) >= min_tokens]

    # --- resolución de la función objetivo ------------------------------
    def buscar_por_referencia(self, ref: str) -> Funcion:
        """ref = 'archivo.py:nombre' o 'archivo.py:nombre:linea'."""
        partes = ref.rsplit(":", 2) if ref.count(":") >= 2 else ref.rsplit(":", 1)
        if len(partes) < 2:
            raise ValueError("formato esperado: archivo.py:nombre_funcion[:linea]")
        archivo, nombre = partes[0].replace("\\", "/"), partes[1]
        linea = int(partes[2]) if len(partes) == 3 else None
        archivo = archivo.removeprefix("./")
        hits = [f for f in self.funciones
                if f.nombre == nombre and (f.archivo == archivo or f.archivo.endswith("/" + archivo))
                and (linea is None or f.linea == linea)]
        if not hits:
            raise LookupError(f"no se encontró la función {nombre!r} en {archivo!r}")
        if len(hits) > 1:
            opciones = ", ".join(f"{h.archivo}:{h.nombre}:{h.linea}" for h in hits)
            raise LookupError(f"referencia ambigua; especificá la línea: {opciones}")
        return hits[0]

    @staticmethod
    def desde_codigo(codigo: str) -> Funcion:
        """Toma la primera función definida en el código pegado."""
        funcs = extraer_de_codigo(codigo, "<codigo>")
        if not funcs:
            raise ValueError("el código provisto no define ninguna función")
        f = funcs[0]
        f.tokens = tokens_de_funcion(f.nodo)
        return f

    # --- buqueda ----------------------------------------------------------
    def score(self, a: Funcion, b: Funcion) -> float:
        return similitud(a.tokens, b.tokens, self.metrica, self.n)

    def top_k(self, objetivo: Funcion, k: int = 5) -> list[Resultado]:
        """Top-K funciones más similares (excluye a la propia función objetivo)."""
        res = [Resultado(f, s, s >= self.umbral)
               for f in self.funciones if f.id != objetivo.id
               for s in [self.score(objetivo, f)]]
        res.sort(key=lambda r: (-r.score, r.funcion.archivo, r.funcion.linea))
        return res[:k]

    def todos_contra_todos(self) -> list[tuple[Funcion, Funcion, float]]:
        """Pares candidatos a duplicado (O(n²)), ordenados por score descendente."""
        pares = [(a, b, s) for a, b in combinations(self.funciones, 2)
                 for s in [self.score(a, b)] if s >= self.umbral]
        return sorted(pares, key=lambda p: -p[2])
