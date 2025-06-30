#!/usr/bin/env python3
import re
from datetime import date
from pathlib import Path

SETUP_PATH = Path('setup.py')
CHANGELOG_PATH = Path('CHANGELOG.md')

VERSION_RE = re.compile(r"version='(\d+\.\d+\.\d+)'")


def read_version():
    content = SETUP_PATH.read_text()
    match = VERSION_RE.search(content)
    if not match:
        raise ValueError('Versión no encontrada en setup.py')
    return match.group(1)


def bump(version: str) -> str:
    parts = version.split('.')
    if len(parts) < 3:
        parts.append('0')
    parts[-1] = str(int(parts[-1]) + 1)
    return '.'.join(parts)


def update_setup(new_version: str):
    content = SETUP_PATH.read_text()
    new_content = VERSION_RE.sub(f"version='{new_version}'", content)
    SETUP_PATH.write_text(new_content)


def update_changelog(new_version: str):
    CHANGELOG_PATH.touch(exist_ok=True)
    existing = CHANGELOG_PATH.read_text()
    today = date.today().isoformat()
    entry = f"## v{new_version} - {today}\n- Cambios pendientes.\n\n"
    CHANGELOG_PATH.write_text(entry + existing)


def main():
    current = read_version()
    new = bump(current)
    update_setup(new)
    update_changelog(new)
    print(new)


if __name__ == '__main__':
    main()
