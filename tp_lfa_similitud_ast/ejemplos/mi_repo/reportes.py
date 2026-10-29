# Clon tipo 2 de promedio (renombrado de variables + literales distintos)
def media_ventas(montos):
    acumulado = 0.0
    n = 0
    for m in montos:
        acumulado += m
        n += 1
    if n == 0:
        return 0.0
    return acumulado / n


# Clon de contar_palabras con dos sentencias independientes reordenadas
def frecuencia_terminos(documento):
    frecuencias = {}
    for termino in documento.split():
        termino = termino.lower()
        if termino not in frecuencias:
            frecuencias[termino] = 0
        frecuencias[termino] += 1
    return frecuencias


def mayor(lista):
    resultado = None
    for elemento in lista:
        if resultado is None or elemento > resultado:
            resultado = elemento
    return resultado


def formatear_reporte(titulo, filas):
    lineas = [titulo.upper(), "-" * len(titulo)]
    for clave, valor in filas:
        lineas.append(f"{clave}: {valor}")
    return "\n".join(lineas)


# Clon de promedio con sentencias independientes reordenadas + renombrado
def ticket_promedio(importes):
    cant = 0
    suma = 0
    for imp in importes:
        cant += 1
        suma += imp
    if cant == 0:
        return 0
    return suma / cant
