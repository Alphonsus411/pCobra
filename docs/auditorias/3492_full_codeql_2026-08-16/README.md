# Evidencia de Full CodeQL 2.26.3 (2026-08-16 UTC)

## Alcance y criterio

Se validaron con el mismo CLI las queries
`.github/codeql/custom/unsafe-eval-exec.ql` y
`.github/codeql/custom/missing-codegen-exception.ql`, los cuatro casos de los
harnesses que el workflow agrupa bajo dos directorios, y el análisis completo
configurado por `.github/codeql/custom/codeql-config.yml`.

No se modificó ninguna query, Lexer ni Parser. El análisis completo llegó a
interpretar los resultados y terminó con código 0; por tanto, en esta ejecución
sí existe evidencia de **Full CodeQL PASS**, no inferida de pruebas unitarias ni
de compilaciones parciales.

## Localización y versión del binario

La búsqueda inicial confirmó que `codeql` no estaba en `PATH` ni preextraído en
los directorios habituales:

```console
$ command -v codeql
[sin salida]
[exit 1]

$ find /opt /usr/local /root /tmp /workspace -iname '*codeql*' 2>/dev/null | head -250
[solo configuración, pruebas y documentación del repositorio; ningún CLI]
[exit 0]
```

Se obtuvo el bundle oficial exacto y se dejó disponible fuera del repositorio:

```console
$ curl -fL --retry 3 --output /tmp/codeql-bundle-2.26.3/codeql-bundle-linux64.tar.gz https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.26.3/codeql-bundle-linux64.tar.gz
100 807M
[exit 0]

$ tar -xzf /tmp/codeql-bundle-2.26.3/codeql-bundle-linux64.tar.gz -C /tmp/codeql-bundle-2.26.3
[sin salida]
[exit 0]

$ /tmp/codeql-bundle-2.26.3/codeql/codeql version
CodeQL command-line toolchain release 2.26.3.
Copyright (C) 2019-2026 GitHub, Inc.
Unpacked in: /tmp/codeql-bundle-2.26.3/codeql
[exit 0]
```

Todas las invocaciones posteriores usaron exclusivamente ese binario.

## Metadata y compilación dirigida

`query compile` validó la metadata requerida y compiló ambas queries. La primera
emitió una advertencia QLDoc no fatal, registrada literalmente; no hubo error de
metadata ni compilación.

```console
$ /tmp/codeql-bundle-2.26.3/codeql/codeql query compile .github/codeql/custom/unsafe-eval-exec.ql
Compiling query plan for /workspace/pCobra/.github/codeql/custom/unsafe-eval-exec.ql.
WARNING: QLDoc comment is not attached to any QL element (/workspace/pCobra/.github/codeql/custom/unsafe-eval-exec.ql:11,1-13,4)
Done [1/1] /workspace/pCobra/.github/codeql/custom/unsafe-eval-exec.ql.
[exit 0]

$ /tmp/codeql-bundle-2.26.3/codeql/codeql query compile .github/codeql/custom/missing-codegen-exception.ql
Compiling query plan for /workspace/pCobra/.github/codeql/custom/missing-codegen-exception.ql.
Done [1/1] /workspace/pCobra/.github/codeql/custom/missing-codegen-exception.ql.
[exit 0]
```

## Harnesses definidos por CI

Se reprodujo literalmente la lista de directorios del paso `Test custom CodeQL
queries` de `.github/workflows/codeql.yml`, sustituyendo únicamente el output
`codeql-path` de la action por la ruta confirmada del CLI:

```console
$ /tmp/codeql-bundle-2.26.3/codeql/codeql test run .github/codeql/custom/test/ast_no_export_validation .github/codeql/custom/test/ast_no_type_validation
Executing 4 tests in 4 directories.
[1/4 ...] PASSED .../ast_no_export_validation/safe/ast-no-export-validation.qlref
[2/4 ...] PASSED .../ast_no_export_validation/insecure/ast-no-export-validation.qlref
[3/4 ...] PASSED .../ast_no_type_validation/safe/ast-no-type-validation.qlref
[4/4 ...] PASSED .../ast_no_type_validation/insecure/ast-no-type-validation.qlref
Completed in 23.1s (extract 11s comp 1.3s eval 2.3s).
All 4 tests passed.
[exit 0]
```

## Inicialización, construcción y análisis completo

Para reproducir `init` con lenguaje Python, su configuración, `autobuild` y la
finalización de la base en una ejecución local equivalente del CLI 2.26.3:

```console
$ /tmp/codeql-bundle-2.26.3/codeql/codeql database create /tmp/pcobra-codeql-db --language=python --build-mode=none --source-root=/workspace/pCobra --codescanning-config=.github/codeql/custom/codeql-config.yml
Processed 1382 modules in 78.41s
Finalizing database at /tmp/pcobra-codeql-db.
TRAP import complete (10.7s).
Finished zipping source archive (1.60 MiB).
Successfully created database at /tmp/pcobra-codeql-db.
[exit 0]
```

El análisis no recibió una suite manual: consumió la configuración de code
scanning almacenada en la base durante la inicialización, igual que el paso
`analyze` de la action:

```console
$ /tmp/codeql-bundle-2.26.3/codeql/codeql database analyze /tmp/pcobra-codeql-db --format=sarif-latest --output=/tmp/pcobra-codeql.sarif --sarif-category=python --threads=0
Compiling query plan for /workspace/pCobra/.github/codeql/custom/ast-no-export-validation.ql.
Compiling query plan for /workspace/pCobra/.github/codeql/custom/ast-no-type-validation.ql.
Compiling query plan for /workspace/pCobra/.github/codeql/custom/missing-codegen-exception.ql.
Compiling query plan for /workspace/pCobra/.github/codeql/custom/unsafe-eval-exec.ql.
WARNING: QLDoc comment is not attached to any QL element (/workspace/pCobra/.github/codeql/custom/unsafe-eval-exec.ql:11,1-13,4)
[45/49 ...] Evaluation done; writing results to custom-queries/ast-no-export-validation.bqrs.
[47/49 ...] Evaluation done; writing results to custom-queries/missing-codegen-exception.bqrs.
[48/49 ...] Evaluation done; writing results to custom-queries/ast-no-type-validation.bqrs.
[49/49 ...] Evaluation done; writing results to custom-queries/unsafe-eval-exec.bqrs.
Shutting down query evaluator.
Interpreting results.
CodeQL scanned 1166 out of 1166 Python files and 16 out of 16 GitHub Actions files in this invocation.
[exit 0]
```

El SARIF resultante quedó en `/tmp/pcobra-codeql.sarif`, fuera del árbol Git.
No apareció un fallo en otra query, por lo que no se activó el criterio de parada.

## Remoto y CI del SHA final

```console
$ git remote -v
[sin salida]
[exit 0]
```

Esta copia no tiene remoto configurado. Por ello no fue posible publicar la rama
ni consultar CI del SHA final; esa limitación no altera el PASS del análisis
completo local, pero **el CI remoto queda NO COMPROBADO**.
