"""Métricas de similitud entre secuencias de tokens (valores en [0, 1])."""
from __future__ import annotations

from collections import Counter

N_POR_DEFECTO = 3  # ver INFORME.md: justificación de n

# Umbral "candidata a duplicado" por métrica, calibrado sobre ejemplos/mi_repo
# (ver INFORME.md). Cada métrica tiene un "piso de ruido" distinto: Levenshtein
# da ~0.4-0.5 entre funciones no relacionadas, Jaccard sobre 3-gramas da < 0.35.
UMBRALES = {"jaccard": 0.50, "levenshtein": 0.70, "combinada": 0.55}
UMBRAL_POR_DEFECTO = UMBRALES["jaccard"]


def ngramas(tokens: list[str], n: int = N_POR_DEFECTO) -> Counter:
    """Multiconjunto de n-gramas. Si la secuencia es más corta que n, se usa entera."""
    if len(tokens) < n:
        return Counter([tuple(tokens)]) if tokens else Counter()
    return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def jaccard(a: list[str], b: list[str], n: int = N_POR_DEFECTO) -> float:
    """Jaccard ponderado (sobre multiconjuntos) de n-gramas: |A∩B| / |A∪B|."""
    ga, gb = ngramas(a, n), ngramas(b, n)
    if not ga and not gb:
        return 1.0
    inter = sum((ga & gb).values())
    union = sum((ga | gb).values())
    return inter / union if union else 0.0


def levenshtein(a: list[str], b: list[str]) -> int:
    """Distancia de edición clásica (programación dinámica, memoria O(min(n,m)))."""
    if len(a) < len(b):
        a, b = b, a
    previa = list(range(len(b) + 1))
    for i, ta in enumerate(a, 1):
        actual = [i]
        for j, tb in enumerate(b, 1):
            actual.append(min(
                previa[j] + 1,                  # borrado
                actual[j - 1] + 1,              # insercion
                previa[j - 1] + (ta != tb),    #  sustitucion
            ))
        previa = actual
    return previa[-1]


def levenshtein_normalizado(a: list[str], b: list[str]) -> float:
    """Similitud = 1 - dist / max(len). 1.0 = idénticas."""
    if not a and not b:
        return 1.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


def combinada(a: list[str], b: list[str], n: int = N_POR_DEFECTO) -> float:
    """Promedio de ambas: Jaccard tolera reordenamientos, Levenshtein premia el orden."""
    return (jaccard(a, b, n) + levenshtein_normalizado(a, b)) / 2


METRICAS = {
    "jaccard": jaccard,
    "levenshtein": lambda a, b, n=N_POR_DEFECTO: levenshtein_normalizado(a, b),
    "combinada": combinada,
}


def similitud(a: list[str], b: list[str], metrica: str = "jaccard",
              n: int = N_POR_DEFECTO) -> float:
    try:
        return METRICAS[metrica](a, b, n)
    except KeyError:
        raise ValueError(f"métrica desconocida: {metrica!r}. Opciones: {list(METRICAS)}")
