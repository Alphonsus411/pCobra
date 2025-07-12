# Funciones para probar presencia de eval y exec


def insecure_eval(data):
    return eval(data)


def insecure_exec(code):
    exec(code)


def test_insecure_eval_exec():
    assert insecure_eval("1 + 1") == 2
    assert insecure_exec("a = 5") is None
