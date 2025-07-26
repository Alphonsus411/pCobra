@ECHO OFF
SETLOCAL ENABLEEXTENSIONS

REM Entrar al directorio del script
pushd %~dp0

REM Configurar comando Sphinx
IF "%SPHINXBUILD%"=="" (
    SET SPHINXBUILD=sphinx-build
)
SET SOURCEDIR=frontend/docs
SET BUILDDIR=frontend/build

REM Verificar que Sphinx esté disponible
where %SPHINXBUILD% >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ No se encontró 'sphinx-build'.
    echo 🔧 Instálalo con: pip install sphinx
    echo O define la variable SPHINXBUILD si lo tienes en otro sitio.
    echo Más info: https://www.sphinx-doc.org/
    exit /b 1
)

REM Mostrar ayuda si no hay argumentos
IF "%1"=="" (
    goto help
)

REM Ejecutar comando Sphinx
%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
ENDLOCAL
