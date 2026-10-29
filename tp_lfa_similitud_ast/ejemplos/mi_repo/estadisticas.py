def promedio(valores):
    """Promedio aritmético."""
    total = 0
    cantidad = 0
    for v in valores:
        total += v
        cantidad += 1
    if cantidad == 0:
        return 0
    return total / cantidad


def maximo(valores):
    mejor = None
    for v in valores:
        if mejor is None or v > mejor:
            mejor = v
    return mejor


def contar_palabras(texto):
    conteo = {}
    for palabra in texto.split():
        palabra = palabra.lower()
        if palabra in conteo:
            conteo[palabra] += 1
        else:
            conteo[palabra] = 1
    return conteo
