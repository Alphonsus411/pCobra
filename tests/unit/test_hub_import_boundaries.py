"""Regresión de la frontera arquitectónica de CobraHub."""

import ast
import importlib
import pkgutil
from pathlib import Path

import pcobra.cobra.hub as hub
from pcobra.cobra.hub.errors import PackageResolutionError
from pcobra.cobra.hub.resolver import CobraDependencyError


def test_hub_no_importa_installer_cli_ni_gui():
    """Hub debe poder evolucionar sin depender de Installer ni presentación."""
    prohibidos = ("pcobra.cobra_installer", "pcobra.cobra.cli", "pcobra.gui")
    for module_info in pkgutil.walk_packages(hub.__path__, f"{hub.__name__}."):
        module = importlib.import_module(module_info.name)
        source = Path(module.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ] + [
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        assert not any(
            imported.startswith(prohibido)
            for imported in imports
            for prohibido in prohibidos
        ), f"{module_info.name} depende de una capa de presentación"


def test_hub_conserva_exports_publicos_del_repositorio():
    assert hub.PackageRepository
    assert hub.HttpCobraHubRepository
    assert hub.DownloadedPackage


def test_error_de_dependencias_pertenece_al_dominio_hub():
    assert issubclass(CobraDependencyError, PackageResolutionError)


def test_servicio_cobrahub_no_importa_cliente_directa_ni_indirectamente():
    """La coordinación no debe regresar a la implementación HTTP del cliente."""
    source_root = Path(__file__).parents[2] / "src"
    graph: dict[str, set[str]] = {}
    for source_path in source_root.rglob("*.py"):
        module = ".".join(source_path.relative_to(source_root).with_suffix("").parts)
        if module.endswith(".__init__"):
            module = module.removesuffix(".__init__")
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
                imports.update(f"{node.module}.{alias.name}" for alias in node.names)
        graph[module] = imports

    pendientes = ["pcobra.cobra.cli.services.cobrahub_service"]
    alcanzables: set[str] = set()
    while pendientes:
        module = pendientes.pop()
        if module in alcanzables:
            continue
        alcanzables.add(module)
        pendientes.extend(graph.get(module, set()) - alcanzables)

    assert "pcobra.cobra.cli.cobrahub_client" not in alcanzables
