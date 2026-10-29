import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simfunc.normalizacion import tokens_de_funcion  # noqa: E402


@pytest.fixture
def tokens():
    """Devuelve los tokens normalizados de la primera función del código dado."""
    def _tokens(codigo: str) -> list[str]:
        nodo = next(n for n in ast.walk(ast.parse(codigo))
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        return tokens_de_funcion(nodo)
    return _tokens


REPO_EJEMPLO = Path(__file__).resolve().parents[1] / "ejemplos" / "mi_repo"
