from pcobra.cobra.stdlib_contract import CONTRACTS, get_contract_manifests
from pcobra.cobra.stdlib_contract.generator import render_contract_markdown


def test_contracts_declaran_campos_minimos_para_module_map():
    manifests = get_contract_manifests()
    modules = {descriptor.module for descriptor in CONTRACTS}
    assert set(manifests) == modules
    for module, manifest in manifests.items():
        assert module.startswith("cobra.")
        assert manifest["public_api"]
        assert isinstance(manifest["backend_preferido"], str)


def test_markdown_generado_incluye_tabla_cobertura_por_funcion():
    markdown = render_contract_markdown()
    assert "Tabla de garantías por módulo" in markdown
    assert "| Módulo | API pública | Backend primario | Fallback | Límites |" in markdown
    assert "Cobertura por función" in markdown
    assert "| Función | Backend | Nivel |" in markdown
    for descriptor in CONTRACTS:
        assert f"| `{descriptor.module}` |" in markdown
        assert f"## `{descriptor.module}`" in markdown
