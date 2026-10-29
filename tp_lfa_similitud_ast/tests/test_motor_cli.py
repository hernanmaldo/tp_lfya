import pytest

import buscar_similares
from simfunc.extraccion import extraer_de_codigo
from simfunc.motor import Motor
from tests.conftest import REPO_EJEMPLO


def test_extraccion_incluye_metodos_async_y_anidadas():
    codigo = "class C:\n    def m(self): pass\n    async def am(self): pass\ndef f():\n    def g(): pass"
    assert {f.nombre for f in extraer_de_codigo(codigo)} == {"m", "am", "f", "g"}


def test_motor_ignora_archivos_con_error_de_sintaxis():
    motor = Motor(REPO_EJEMPLO)
    assert motor.funciones and all("roto.py" not in f.archivo for f in motor.funciones)


def test_top_k_encuentra_los_clones_y_excluye_al_objetivo():
    motor = Motor(REPO_EJEMPLO)
    obj = motor.buscar_por_referencia("estadisticas.py:promedio")
    res = motor.top_k(obj, k=3)
    assert len(res) == 3 and all(r.funcion.id != obj.id for r in res)
    assert {r.funcion.nombre for r in res if r.candidata} == {"media_ventas", "ticket_promedio"}
    assert res[0].score >= res[1].score >= res[2].score


def test_referencia_inexistente():
    with pytest.raises(LookupError):
        Motor(REPO_EJEMPLO).buscar_por_referencia("estadisticas.py:no_existe")


def test_cli_por_referencia(capsys):
    rc = buscar_similares.main(["--dir", str(REPO_EJEMPLO),
                                "--funcion", "estadisticas.py:maximo", "--top", "2"])
    salida = capsys.readouterr().out
    assert rc == 0 and "reportes.py:mayor" in salida


def test_cli_codigo_pegado(capsys):
    rc = buscar_similares.main(["--dir", str(REPO_EJEMPLO), "--top", "1",
                                "--codigo", "def z(k):\n    if k <= 1:\n        return 1\n    return k * z(k - 1)"])
    assert rc == 0 and "factorial" in capsys.readouterr().out


def test_cli_duplicados(capsys):
    assert buscar_similares.main(["--dir", str(REPO_EJEMPLO), "--duplicados"]) == 0
    assert "Pares candidatos a duplicado: 5" in capsys.readouterr().out
