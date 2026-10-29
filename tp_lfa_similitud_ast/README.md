# Motor de búsqueda de funciones similares vía AST

Trabajo Práctico — Lenguajes Formales y Autómatas 2026 (UCSE).

Dado un directorio con archivos `.py`, la herramienta extrae todas las funciones, normaliza su
AST (variables → `VARn`, literales → `LIT`), lo serializa en pre-order a una secuencia de tokens
y busca las funciones estructuralmente más similares a una función objetivo.

## Requisitos
- Python ≥ 3.9 (usa `ast.unparse`). Sin dependencias externas para ejecutar.
- `pytest` para los tests: `pip install -r requirements.txt`

## Estructura
```
buscar_similares.py        CLI
simfunc/
  extraccion.py            recorrido del directorio + ast.parse + FunctionDef/AsyncFunctionDef
  normalizacion.py         NodeTransformer (VARn / LIT) + serialización pre-order
  similitud.py             Jaccard sobre n-gramas, Levenshtein normalizado, combinada, umbrales
  motor.py                 indexación, top-K y comparación todos-contra-todos
tests/                     suite pytest (positivos, negativos, normalización, métricas, CLI)
ejemplos/mi_repo/          repositorio de ejemplo con clones plantados (incluye un .py roto)
INFORME.md                 informe (decisiones, métrica, limitaciones, mejoras)
```

## Uso
```bash
# función objetivo por archivo:nombre (agregar :linea si el nombre está repetido)
python buscar_similares.py --dir ejemplos/mi_repo --funcion estadisticas.py:promedio --top 5

# función objetivo pegando el código (o '-' para leer de stdin)
python buscar_similares.py --dir ejemplos/mi_repo --codigo "def f(xs):
    t = 0
    for x in xs:
        t += x
    return t"

# desde un archivo con el código
python buscar_similares.py --dir ejemplos/mi_repo --codigo-archivo snippet.py

# todos-contra-todos: pares candidatos a duplicado
python buscar_similares.py --dir ejemplos/mi_repo --duplicados
```

Opciones: `--metrica {jaccard,levenshtein,combinada}` (default `jaccard`), `--n` (default 3),
`--umbral` (default según métrica), `--min-tokens`, `--debug` (muestra AST normalizado y tokens),
`-v` (avisa archivos omitidos por error de sintaxis).

Salida de ejemplo:
```
Funciones indexadas: 17 | métrica=jaccard n=3 | umbral=0.5
Objetivo: estadisticas.py:promedio (l.1) - 48 tokens

 #   score  dup?  función
 1   1.000  SÍ    reportes.py:media_ventas (l.2)
 2   0.559  SÍ    reportes.py:ticket_promedio (l.40)
 3   0.188        estadisticas.py:contar_palabras (l.21)
```

## Tests
```bash
python -m pytest -v
```
