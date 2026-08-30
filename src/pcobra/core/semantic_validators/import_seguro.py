from pathlib import Path
from os import PathLike

from .base import ValidadorBase
from ..ast_nodes import NodoImport
from .primitiva_peligrosa import PrimitivaPeligrosaError


class ValidadorImportSeguro(ValidadorBase):
    """Valida que las instrucciones import sean seguras."""

    def __init__(
        self,
        *,
        main_file: str | PathLike[str] | None = None,
        project_root: str | PathLike[str] | None = None,
    ) -> None:
        super().__init__()
        self._main_file = (
            Path(main_file).expanduser().resolve(strict=False)
            if main_file is not None
            else None
        )
        self._project_root = (
            Path(project_root).expanduser().resolve(strict=False)
            if project_root is not None
            else None
        )

    def visit_import(self, nodo: NodoImport) -> None:
        from .. import interpreter as interpreter_module
        from ..import_utils import ruta_import_permitida

        ruta = Path(nodo.ruta).expanduser()
        if not ruta.is_absolute() and self._main_file is not None:
            ruta = self._main_file.parent / ruta

        ruta_validacion = str(ruta.resolve(strict=False))
        whitelist = {str(ruta) for ruta in interpreter_module.IMPORT_WHITELIST}

        if self._project_root is not None:
            whitelist.add(str(self._project_root))

        interpreter_module._sincronizar_config_import()

        if not ruta_import_permitida(
            ruta_validacion,
            (
                str(interpreter_module.MODULES_PATH)
                if interpreter_module.MODULES_PATH is not None
                else None
            ),
            whitelist,
        ):
            raise PrimitivaPeligrosaError(
                f"Importación de módulo no permitida: {nodo.ruta}"
            )

        self.generic_visit(nodo)
