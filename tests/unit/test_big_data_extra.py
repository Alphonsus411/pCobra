"""Pruebas ligeras para el extra opcional de big data."""

from importlib import import_module

from packaging.version import Version


def test_dask_modern_version():
    """Comprueba que Dask se pueda importar y cumpla la versión mínima."""

    dask = import_module("dask")
    assert Version(dask.__version__) >= Version("2024.6.2")
