import ast
import threading
from pathlib import Path
from types import SimpleNamespace

from pcobra.cobra_installer import idle_bridge
from pcobra.gui import idle, runtime


class Control(SimpleNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(args=args, **kwargs)
        if args and "text" not in kwargs:
            self.text = args[0]
        if "controls" not in kwargs:
            self.controls = list(args[0]) if args and isinstance(args[0], list) else []

    def update(self):
        return None


class FakeFlet:
    class Icons:
        INSERT_DRIVE_FILE = "file"
        FOLDER = "folder"

    class ScrollMode:
        ALWAYS = "always"

    TextField = Control
    Text = Control
    Dropdown = Control
    Switch = Control
    ElevatedButton = Control
    TextButton = Control
    Row = Control
    Column = Control
    Container = Control
    ListView = Control
    ListTile = Control
    ExpansionTile = Control
    Icon = Control
    AlertDialog = Control
    Option = Control


class FakePage:
    def __init__(self):
        self.controls = []
        self.dialog = None
        self.update_count = 0
        self.launched_urls = []

    def add(self, control):
        self.controls.append(control)

    def update(self):
        self.update_count += 1

    def launch_url(self, url):
        self.launched_urls.append(url)


class ImmediateThread:
    def __init__(self, target, daemon=None):
        self.target = target
        self.daemon = daemon

    def start(self):
        self.target()


def walk_controls(control):
    yield control
    for attr in ("controls", "actions"):
        for child in getattr(control, attr, []) or []:
            yield from walk_controls(child)
    content = getattr(control, "content", None)
    if content is not None:
        yield from walk_controls(content)
    title = getattr(control, "title", None)
    if title is not None:
        yield from walk_controls(title)


def find_button(root, text):
    for control in walk_controls(root):
        if getattr(control, "text", None) == text and callable(
            getattr(control, "on_click", None)
        ):
            return control
    raise AssertionError(f"No se encontró el botón {text!r}")


def test_boton_empaquetar_detecta_proyecto_pide_opciones_y_muestra_progreso(
    monkeypatch, tmp_path
):
    workspace = tmp_path / "workspace"
    project = workspace / "proyecto_activo"
    project.mkdir(parents=True)
    active_file = project / "programa.cobra"
    active_file.write_text("imprimir('hola')", encoding="utf-8")

    package_calls = []

    def fake_package_current_project(project_path, ui_options, progress_callback=None):
        package_calls.append((Path(project_path), dict(ui_options), progress_callback))
        progress_callback("Progreso mock: generando ejecutable")
        dist_dir = Path(project_path) / "dist"
        artifact_path = dist_dir / "proyecto_activo"
        return SimpleNamespace(
            dist_dir=dist_dir,
            output_dir=None,
            artifact_path=artifact_path,
        )

    monkeypatch.setattr(runtime, "require_flet", lambda: FakeFlet)
    monkeypatch.setattr(runtime, "resolver_workspace_root_idle", lambda: workspace)
    monkeypatch.setattr(runtime, "listar_directorio_idle", lambda _root: [])
    monkeypatch.setattr(threading, "Thread", ImmediateThread)
    monkeypatch.setattr(
        idle_bridge, "package_current_project", fake_package_current_project
    )

    page = FakePage()
    idle.main(page)

    root = SimpleNamespace(controls=page.controls)
    ruta_input = next(
        control
        for control in walk_controls(root)
        if getattr(control, "label", None) == "Ruta"
    )
    ruta_input.value = str(active_file)

    find_button(root, "Empaquetar").on_click(None)

    dialog = page.dialog
    assert dialog is not None
    assert dialog.open is True
    assert "proyecto_activo" in dialog.content.controls[0].value

    nombre_input = next(
        control
        for control in walk_controls(dialog)
        if getattr(control, "label", None) == "Nombre del ejecutable"
    )
    nombre_input.value = "cobra_gui_test"
    selector_modo = next(
        control
        for control in walk_controls(dialog)
        if getattr(control, "label", None) == "Formato"
    )
    selector_modo.value = "onefile"

    find_button(dialog, "Empaquetar").on_click(None)

    assert len(package_calls) == 1
    project_path, ui_options, progress_callback = package_calls[0]
    assert project_path == project
    assert ui_options == {
        "name": "cobra_gui_test",
        "target": "current",
        "mode": "onefile",
        "icon": None,
    }
    assert callable(progress_callback)
    assert (
        f"Empaquetado finalizado: {project / 'dist' / 'proyecto_activo'}"
        in dialog.content.controls[0].value
    )
    salida = next(
        control
        for control in walk_controls(root)
        if getattr(control, "selectable", None) is True
    )
    assert "Iniciando empaquetado" in salida.value
    assert "Progreso mock: generando ejecutable" in salida.value
    assert (
        f"Empaquetado finalizado: {project / 'dist' / 'proyecto_activo'}"
        in salida.value
    )
    assert page.launched_urls == [(project / "dist").resolve().as_uri()]


def test_idle_no_importa_modulos_internos_de_cobra_installer():
    source = Path(idle.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    cobra_installer_imports = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("pcobra.cobra_installer")
        ):
            cobra_installer_imports.append(node.module)
        elif isinstance(node, ast.Import):
            cobra_installer_imports.extend(
                alias.name
                for alias in node.names
                if alias.name.startswith("pcobra.cobra_installer")
            )

    assert cobra_installer_imports == ["pcobra.cobra_installer.idle_bridge"]
