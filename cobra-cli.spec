# -*- mode: python ; coding: utf-8 -*-
import os
import shutil

# Asegurar compilaciones deterministas
os.environ["SOURCE_DATE_EPOCH"] = os.getenv("SOURCE_DATE_EPOCH", "0")
# Limpiar directorios como si se pasara --clean
for path in ("build", "dist"):
    if os.path.isdir(path):
        shutil.rmtree(path)

a = Analysis(
    ['src\\cobra\\cli\\cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cobra-cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
