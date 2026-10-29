"""Casos exigidos por el enunciado: 2+ positivos y 2+ negativos."""
import pytest

from simfunc.similitud import UMBRALES, similitud

PROMEDIO = '''
def promedio(valores):
    total = 0
    cantidad = 0
    for v in valores:
        total += v
        cantidad += 1
    if cantidad == 0:
        return 0
    return total / cantidad
'''

# Positivo 1: clon tipo 2 - variables, parámetros, nombre y literales cambiados
PROMEDIO_RENOMBRADO = '''
def media_ventas(montos):
    """Docstring que no debe influir."""
    acumulado = 0.0
    n = 0
    for m in montos:
        acumulado += m
        n += 1
    if n == 0:
        return -1.0
    return acumulado / n
'''

# Positivo 2: líneas independientes reordenadas (+ renombrado)
PROMEDIO_REORDENADO = '''
def ticket_promedio(importes):
    cant = 0
    suma = 0
    for imp in importes:
        cant += 1
        suma += imp
    if cant == 0:
        return 0
    return suma / cant
'''

CONTAR = '''
def contar_palabras(texto):
    conteo = {}
    for palabra in texto.split():
        palabra = palabra.lower()
        if palabra in conteo:
            conteo[palabra] += 1
        else:
            conteo[palabra] = 1
    return conteo
'''

# Positivo 3: rama if/else invertida y renombrado
CONTAR_INVERTIDO = '''
def frec(doc):
    f = {}
    for t in doc.split():
        t = t.lower()
        if t not in f:
            f[t] = 1
        else:
            f[t] += 1
    return f
'''

# Negativos: funciones claramente distintas
LEER_JSON = '''
def leer_json(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta)
    with open(ruta, encoding="utf-8") as fh:
        return json.load(fh)
'''

FORMATEAR = '''
def formatear_reporte(titulo, filas):
    lineas = [titulo.upper(), "-" * len(titulo)]
    for clave, valor in filas:
        lineas.append(f"{clave}: {valor}")
    return "\\n".join(lineas)
'''

FACTORIAL = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''

POSITIVOS = [
    ("renombrado", PROMEDIO, PROMEDIO_RENOMBRADO),
    ("reordenado", PROMEDIO, PROMEDIO_REORDENADO),
    ("if_invertido", CONTAR, CONTAR_INVERTIDO),
]
NEGATIVOS = [
    ("promedio_vs_leer_json", PROMEDIO, LEER_JSON),
    ("contar_vs_factorial", CONTAR, FACTORIAL),
    ("promedio_vs_formatear", PROMEDIO, FORMATEAR),
]
METRICAS = list(UMBRALES)


@pytest.mark.parametrize("metrica", METRICAS)
@pytest.mark.parametrize("caso,a,b", POSITIVOS, ids=[p[0] for p in POSITIVOS])
def test_positivos_superan_umbral(tokens, metrica, caso, a, b):
    s = similitud(tokens(a), tokens(b), metrica)
    assert s >= UMBRALES[metrica], f"{caso}: {s:.3f} < {UMBRALES[metrica]}"


@pytest.mark.parametrize("metrica", METRICAS)
@pytest.mark.parametrize("caso,a,b", NEGATIVOS, ids=[n[0] for n in NEGATIVOS])
def test_negativos_no_superan_umbral(tokens, metrica, caso, a, b):
    s = similitud(tokens(a), tokens(b), metrica)
    assert s < UMBRALES[metrica], f"{caso}: {s:.3f} >= {UMBRALES[metrica]}"


def test_clon_exacto_tipo2_es_identico(tokens):
    assert tokens(PROMEDIO) == tokens(PROMEDIO_RENOMBRADO)
