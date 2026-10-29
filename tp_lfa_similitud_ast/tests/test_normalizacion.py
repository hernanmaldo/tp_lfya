import ast

from simfunc.normalizacion import normalizar


def test_nombre_de_funcion_no_influye(tokens):
    assert tokens("def a(x): return x + 1") == tokens("def otro_nombre(x): return x + 1")


def test_correspondencia_de_variables_se_preserva(tokens):
    # x + x  !=  x + y : la normalización conserva qué ocurrencias son la misma variable
    assert tokens("def f(x, y): return x + x") != tokens("def f(x, y): return x + y")
    assert tokens("def f(a, b): return a + a") == tokens("def g(p, q): return p + p")


def test_literales_se_reemplazan_por_LIT(tokens):
    t = tokens("def f(): return 'hola' + str(42)")
    assert "LIT" in t and "'hola'" not in t and "42" not in t
    assert tokens("def f(): return 1") == tokens("def f(): return 'x'")


def test_none_true_false_se_preservan(tokens):
    assert tokens("def f(): return None") != tokens("def f(): return 0")
    assert "True" in tokens("def f():\n    while True:\n        pass")


def test_docstring_y_anotaciones_no_influyen(tokens):
    con = 'def f(x: int) -> int:\n    """doc"""\n    return x'
    assert tokens(con) == tokens("def f(x):\n    return x")


def test_builtins_y_atributos_se_preservan(tokens):
    t = tokens("def f(xs): return len(xs.keys())")
    assert "len" in t and ".keys" in t


def test_normalizar_no_modifica_el_original():
    nodo = ast.parse("def f(a): return a").body[0]
    normalizar(nodo)
    assert nodo.name == "f" and nodo.args.args[0].arg == "a"


def test_funcion_anidada_se_normaliza():
    nodo = ast.parse("def f(a):\n    def interna(b):\n        return a + b\n    return interna(1)").body[0]
    codigo = ast.unparse(normalizar(nodo))
    assert "interna" not in codigo and "VAR2" in codigo
