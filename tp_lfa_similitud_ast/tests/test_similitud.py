import pytest

from simfunc.similitud import jaccard, levenshtein, levenshtein_normalizado, ngramas, similitud


def test_levenshtein_clasico():
    assert levenshtein(list("kitten"), list("sitting")) == 3
    assert levenshtein([], list("abc")) == 3


@pytest.mark.parametrize("f", [jaccard, levenshtein_normalizado])
def test_propiedades_basicas(f):
    a, b = list("abcdef"), list("xyzuvw")
    assert f(a, a) == 1.0
    assert f(a, b) == f(b, a)
    assert 0.0 <= f(a, b) <= 1.0


def test_ngramas_secuencia_corta():
    assert sum(ngramas(["a", "b"], 3).values()) == 1


def test_metrica_invalida():
    with pytest.raises(ValueError):
        similitud(["a"], ["a"], "coseno")
