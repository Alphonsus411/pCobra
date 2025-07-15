#!/usr/bin/env python3
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

PYPROJECT_PATH = Path("pyproject.toml")
CHANGELOG_PATH = Path("CHANGELOG.md")

# Archivos en los que se actualizará la versión
FILES_TO_UPDATE = [
    PYPROJECT_PATH,
    Path("README.md"),
    Path("MANUAL_COBRA.md"),
    Path("backend/src/jupyter_kernel/__init__.py"),
    Path("frontend/docs/avances.rst"),
    Path("tests/unit/test_cli_plugins_cmd.py"),
]



def read_version() -> str:
    """Obtiene la versión actual del proyecto."""
    if PYPROJECT_PATH.exists():
        data = tomllib.loads(PYPROJECT_PATH.read_text())
        project = data.get("project", {})
        if "version" in project:
            return str(project["version"])

    raise ValueError("Versión no encontrada en pyproject.toml")


def bump(version: str, part: str = "patch") -> str:
    """Incrementa la versión según la parte indicada."""
    parts = [int(p) for p in version.split(".")]
    while len(parts) < 3:
        parts.append(0)

    if part == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif part == "minor":
        parts[1] += 1
        parts[2] = 0
    else:
        parts[2] += 1

    return "{}".format(".".join(str(p) for p in parts))


def update_files(current: str, new_version: str) -> None:
    """Reemplaza la versión en todos los archivos listados."""
    short_current = ".".join(current.split(".")[:2])
    short_new = ".".join(new_version.split(".")[:2])

    for path in FILES_TO_UPDATE:
        if not path.exists():
            continue
        text = path.read_text()
        text = text.replace(current, new_version)
        text = re.sub(rf"\b{re.escape(short_current)}\b", short_new, text)
        if short_current == short_new:
            text = re.sub(rf"Versión {re.escape(short_current)}(?![\.\d])", f"Versión {new_version}", text)
        else:
            text = re.sub(rf"Versión {re.escape(short_current)}", f"Versión {short_new}", text)
        text = re.sub(
            rf"(implementation_version\s*=\s*\"|language_version\s*=\s*\"){re.escape(short_current)}(\")",
            rf"\g<1>{new_version}\g<2>",
            text,
        )
        text = re.sub(rf"version\s*=\s*\"{re.escape(short_current)}\"", f'version = "{new_version}"', text)
        text = text.replace(f"dummy {short_current}", f"dummy {new_version}")
        path.write_text(text)


def update_changelog(new_version: str):
    CHANGELOG_PATH.touch(exist_ok=True)
    existing = CHANGELOG_PATH.read_text()
    today = date.today().isoformat()
    entry = f"## v{new_version} - {today}\n- Cambios pendientes.\n\n"
    CHANGELOG_PATH.write_text(entry + existing)


def main():
    part = sys.argv[1] if len(sys.argv) > 1 else "patch"
    current = read_version()
    new = bump(current, part)
    update_files(current, new)
    update_changelog(new)
    print(new)


if __name__ == '__main__':
    main()
