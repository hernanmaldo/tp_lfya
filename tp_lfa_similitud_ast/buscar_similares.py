#!/usr/bin/env python3
"""CLI del motor de búsqueda de funciones similares vía AST.

Ejemplos:
  python buscar_similares.py --dir ./mi_repo --funcion archivo.py:mi_funcion --top 5
  python buscar_similares.py --dir ./mi_repo --codigo-archivo snippet.py --metrica combinada
  python buscar_similares.py --dir ./mi_repo --codigo "def f(a): return a + 1"
  python buscar_similares.py --dir ./mi_repo --duplicados
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from simfunc.motor import Motor
from simfunc.normalizacion import normalizar
from simfunc.similitud import METRICAS, N_POR_DEFECTO, UMBRALES


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Busca funciones estructuralmente similares (AST).")
    p.add_argument("--dir", required=True, help="directorio (repositorio) a analizar")
    obj = p.add_mutually_exclusive_group(required=True)
    obj.add_argument("--funcion", help="función objetivo: archivo.py:nombre[:linea]")
    obj.add_argument("--codigo", help="código de la función objetivo ('-' = leer de stdin)")
    obj.add_argument("--codigo-archivo", help="archivo con el código de la función objetivo")
    obj.add_argument("--duplicados", action="store_true",
                     help="lista todos los pares candidatos a duplicado (todos-contra-todos)")
    p.add_argument("--top", type=int, default=5, help="cantidad de resultados (K). Default 5")
    p.add_argument("--metrica", choices=list(METRICAS), default="jaccard")
    p.add_argument("--n", type=int, default=N_POR_DEFECTO, help="tamaño de n-grama (Jaccard)")
    p.add_argument("--umbral", type=float, default=None,
                   help="score mínimo para 'candidata a duplicado' "
                        f"(default según métrica: {UMBRALES})")
    p.add_argument("--min-tokens", type=int, default=0,
                   help="ignora funciones con menos tokens (evita ruido de funciones triviales)")
    p.add_argument("--debug", action="store_true",
                   help="muestra el AST normalizado (ast.unparse) y los tokens del objetivo")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    if not Path(args.dir).is_dir():
        print(f"error: {args.dir!r} no es un directorio", file=sys.stderr)
        return 2

    motor = Motor(args.dir, args.metrica, args.n, args.umbral, args.min_tokens, args.verbose)
    print(f"Funciones indexadas: {len(motor.funciones)} | métrica={args.metrica}"
          f"{f' n={args.n}' if args.metrica != 'levenshtein' else ''} | umbral={motor.umbral}")

    if args.duplicados:
        pares = motor.todos_contra_todos()
        print(f"Pares candidatos a duplicado: {len(pares)}\n")
        for a, b, s in pares:
            print(f"{s:6.3f}  {a.archivo}:{a.nombre} (l.{a.linea})  <->  "
                  f"{b.archivo}:{b.nombre} (l.{b.linea})")
        return 0

    try:
        if args.funcion:
            objetivo = motor.buscar_por_referencia(args.funcion)
        else:
            ruta_rel = None
            if args.codigo_archivo:
                ruta = Path(args.codigo_archivo).resolve()
                codigo = ruta.read_text(encoding="utf-8")
                try:
                    ruta_rel = ruta.relative_to(Path(args.dir).resolve()).as_posix()
                except ValueError:
                    pass  # el archivo está fuera del repo analizado
            else:
                codigo = sys.stdin.read() if args.codigo == "-" else args.codigo
            objetivo = Motor.desde_codigo(codigo)
            if ruta_rel:
                objetivo.archivo = ruta_rel  # mismo id que el indexado -> se autoexcluye
            n_funcs = codigo.count("def ")  # aproximado, solo para el aviso
            if n_funcs > 1:
                print(f"[aviso] el código define varias funciones; se usa la primera: "
                      f"{objetivo.nombre}", file=sys.stderr)
    except (ValueError, LookupError, SyntaxError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"Objetivo: {objetivo.archivo}:{objetivo.nombre} (l.{objetivo.linea}) "
          f"- {len(objetivo.tokens)} tokens\n")
    if args.debug:
        print("AST normalizado:\n" + ast.unparse(normalizar(objetivo.nodo)) + "\n")
        print("Tokens:", " ".join(objetivo.tokens), "\n")

    resultados = motor.top_k(objetivo, args.top)
    print(f"{'#':>2}  {'score':>6}  {'dup?':4}  función")
    for i, r in enumerate(resultados, 1):
        f = r.funcion
        print(f"{i:>2}  {r.score:6.3f}  {'SÍ' if r.candidata else '  ':4}  "
              f"{f.archivo}:{f.nombre} (l.{f.linea})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
