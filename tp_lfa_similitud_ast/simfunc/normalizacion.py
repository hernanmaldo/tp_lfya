"""Normalización del AST y serialización pre-order a secuencia de tokens.

Reglas:
  * Parámetros y variables locales -> VAR1, VAR2, ... en orden de primera aparición
    (pre-order), conservando la correspondencia dentro de la función.
  * Literales (números -incluidos negativos-, strings, bytes, f-strings) -> LIT. Se preservan None/True/False
    porque tienen semántica de control (p.ej. `return None`, `while True`).
  * El nombre de la función NO se emite. Tampoco el docstring.
  * Se conservan los builtins (len, range, print, ...) y los nombres de atributos
    (.append, .items, ...): aportan semántica y no suelen cambiar entre clones.
  * Se omite el contexto (Load/Store/Del) porque es redundante con la posición.
"""
from __future__ import annotations

import ast
import builtins
import copy

BUILTINS = frozenset(dir(builtins))
CONSTANTES_SEMANTICAS = (None, True, False, Ellipsis)


class Normalizador(ast.NodeTransformer):
    """Reemplaza identificadores por VARn y literales por LIT."""

    def __init__(self, preservar_builtins: bool = True):
        self.mapa: dict[str, str] = {}
        self.preservar_builtins = preservar_builtins

    def _var(self, nombre: str) -> str:
        if nombre not in self.mapa:
            self.mapa[nombre] = f"VAR{len(self.mapa) + 1}"
        return self.mapa[nombre]

    # --- identificadores -------------------------------------------------
    def visit_arg(self, node: ast.arg):
        node.arg = self._var(node.arg)
        node.annotation = None  # las anotaciones de tipo no cambian el comportamiento
        return node

    def visit_Name(self, node: ast.Name):
        es_builtin = node.id in BUILTINS and node.id not in self.mapa
        if not (self.preservar_builtins and es_builtin):
            node.id = self._var(node.id)
        return node

    def visit_FunctionDef(self, node):
        # funciones anidadas: su nombre es una variable local más
        node.name = self._var(node.name)
        return self._visitar_cuerpo_funcion(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Global(self, node: ast.Global):
        node.names = [self._var(n) for n in node.names]
        return node

    visit_Nonlocal = visit_Global

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.name:
            node.name = self._var(node.name)
        self.generic_visit(node)
        return node

    # --- literales ---------------------------------------------------------
    def visit_Constant(self, node: ast.Constant):
        if not any(node.value is c for c in CONSTANTES_SEMANTICAS):
            node.value = "LIT"
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp):
        # -1, +2.5: el parser los genera como UnaryOp(Constant); se tratan como literal
        if (isinstance(node.op, (ast.USub, ast.UAdd)) and isinstance(node.operand, ast.Constant)
                and isinstance(node.operand.value, (int, float, complex))
                and not isinstance(node.operand.value, bool)):
            return ast.copy_location(ast.Constant(value="LIT"), node)
        self.generic_visit(node)
        return node

    def visit_JoinedStr(self, node: ast.JoinedStr):
        # f-strings: se reemplazan por un literal (las expresiones internas se pierden)
        return ast.copy_location(ast.Constant(value="LIT"), node)

    # --- utilidades --------------------------------------------------------
    def _visitar_cuerpo_funcion(self, node):
        node.decorator_list = []
        node.returns = None
        node.body = quitar_docstring(node.body)
        self.generic_visit(node)
        return node

    def normalizar_funcion(self, nodo_funcion):
        """Normaliza la función raíz (sin usar ni emitir su nombre)."""
        nodo = copy.deepcopy(nodo_funcion)
        nodo.name = "_"  # el nombre propio no influye
        return self._visitar_cuerpo_funcion(nodo)


def quitar_docstring(cuerpo: list[ast.stmt]) -> list[ast.stmt]:
    if (cuerpo and isinstance(cuerpo[0], ast.Expr)
            and isinstance(cuerpo[0].value, ast.Constant)
            and isinstance(cuerpo[0].value.value, str)):
        resto = cuerpo[1:]
        return resto or [ast.Pass()]
    return cuerpo


def normalizar(nodo_funcion, preservar_builtins: bool = True):
    """Devuelve una copia normalizada del AST de la función."""
    return Normalizador(preservar_builtins).normalizar_funcion(nodo_funcion)


# --- serialización pre-order --------------------------------------------------
def _etiqueta(nodo: ast.AST) -> list[str]:
    """Tokens que emite un nodo: su tipo + su valor normalizado si corresponde."""
    tipo = type(nodo).__name__
    if isinstance(nodo, ast.Name):
        return [tipo, nodo.id]
    if isinstance(nodo, ast.arg):
        return [tipo, nodo.arg]
    if isinstance(nodo, ast.Constant):
        return [tipo, "LIT" if nodo.value == "LIT" else repr(nodo.value)]
    if isinstance(nodo, ast.Attribute):
        return [tipo, "." + nodo.attr]
    if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [tipo, nodo.name]
    if isinstance(nodo, ast.keyword):
        return [tipo, f"{nodo.arg}="]
    return [tipo]


def serializar(nodo: ast.AST, raiz: bool = True) -> list[str]:
    """Recorrido pre-order del AST normalizado -> lista lineal de tokens."""
    tokens: list[str] = []
    if raiz and isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
        tokens.append(type(nodo).__name__)  # la raíz NO emite el nombre
    else:
        tokens.extend(_etiqueta(nodo))
    for hijo in ast.iter_child_nodes(nodo):
        if isinstance(hijo, ast.expr_context):
            continue
        tokens.extend(serializar(hijo, raiz=False))
    return tokens


def tokens_de_funcion(nodo_funcion, preservar_builtins: bool = True) -> list[str]:
    """Atajo: normaliza y serializa."""
    return serializar(normalizar(nodo_funcion, preservar_builtins))
