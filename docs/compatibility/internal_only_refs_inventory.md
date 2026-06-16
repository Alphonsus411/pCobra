# Inventario histórico de referencias legacy (go/cpp/java/wasm/asm)

Este reporte se genera con `scripts/ci/generate_internal_only_inventory.py`.

## Método

1. **Búsqueda por path**: se recorren archivos de texto fuera de rutas internas permitidas.
2. **Búsqueda por símbolos**: detección de tokens directos, flags (`--backend`/`--tipo`) y claves de registro.

## Rutas internas excluidas

- `src/pcobra/cobra/cli/internal_compat/`
- `docs/compatibility/`
- `docs/historico/`
- `docs/migracion_targets_retirados.md`
- `docs/migracion_cli_unificada.md`
- `tests/`

## Resumen

- Hallazgos fuera de rutas internas: **1341**.
- Archivos afectados: **601**.

### Hallazgos por símbolo

- `backend_flag`: 0
- `registry_key`: 0
- `target_token`: 1341

### Top paths con más hallazgos

| path | hallazgos |
|---|---:|
| `.venv-release-test/Lib/site-packages/pcobra/cobra/transpilers/compatibility_matrix.py` | 47 |
| `.venv-release-test/Lib/site-packages/prompt_toolkit/key_binding/bindings/vi.py` | 30 |
| `.venv-release-test/Lib/site-packages/numpy/core/tests/test_umath.py` | 25 |
| `.venv-release-test/Lib/site-packages/pcobra/cobra/architecture/legacy_backend_lifecycle.py` | 20 |
| `.venv-release-test/Lib/site-packages/pcobra/cobra/benchmarks/targets_policy.py` | 19 |
| `.venv-release-test/Lib/site-packages/pcobra/cobra/qa/syntax_validation.py` | 19 |
| `src/pcobra/cobra/qa/legacy_syntax_validation.py` | 19 |
| `docs/proposals/plan_nuevas_funcionalidades.md` | 18 |
| `.venv-release-test/Lib/site-packages/pcobra/cobra/transpilers/library_compatibility.py` | 17 |
| `src/pcobra/cobra/transpilers/library_compatibility.py` | 17 |
| `.venv-release-test/Lib/site-packages/prompt_toolkit/buffer.py` | 14 |
| `scripts/generar_matriz_transpiladores.py` | 14 |
| `.venv-release-test/Lib/site-packages/pcobra/cobra/transpilers/legacy/runtime_legacy_tables.py` | 12 |
| `.venv-release-test/Lib/site-packages/pcobra/cobra/semantico/cobra_mod_schema.yaml` | 10 |
| `.venv-release-test/Lib/site-packages/pydantic/v1/schema.py` | 10 |
| `.venv-release-test/Lib/site-packages/pygments/lexers/parsers.py` | 10 |
| `arbol_directorios_limpio.txt` | 10 |
| `docs/_generated/runtime_api_matrix.json` | 10 |
| `docs/_generated/runtime_api_matrix.md` | 10 |
| `scripts/audit_retired_targets.py` | 10 |
| `src/pcobra/cobra/semantico/cobra_mod_schema.yaml` | 10 |
| `.venv-release-test/Lib/site-packages/pcobra/corelibs/__init__.py` | 9 |
| `.venv-release-test/Lib/site-packages/pip/_vendor/pygments/lexers/_mapping.py` | 9 |
| `.venv-release-test/Lib/site-packages/pygments/lexers/_mapping.py` | 9 |
| `CONTRIBUTING.md` | 9 |

### Muestra de hallazgos

| path | línea | símbolo | extracto |
|---|---:|---|---|
| `.venv-release-test/Lib/site-packages/PIL/EpsImagePlugin.py` | 114 | `target_token` | `# go back` |
| `.venv-release-test/Lib/site-packages/PIL/EpsImagePlugin.py` | 195 | `target_token` | `# go to offset - start of "%!PS"` |
| `.venv-release-test/Lib/site-packages/PIL/Image.py` | 2705 | `target_token` | `# writer needs to go back and edit the written data.` |
| `.venv-release-test/Lib/site-packages/PIL/Jpeg2KImagePlugin.py` | 48 | `target_token` | `# Inside box contents: ensure read does not go past box boundaries` |
| `.venv-release-test/Lib/site-packages/PIL/PngImagePlugin.py` | 798 | `target_token` | `# difficult to break if things go wrong in the decoder...` |
| `.venv-release-test/Lib/site-packages/PIL/TiffImagePlugin.py` | 1607 | `target_token` | `# Offset in the tile tuple is 0, we go from 0,0 to` |
| `.venv-release-test/Lib/site-packages/attr/_make.py` | 128 | `target_token` | `Consider using `attrs.field` in new code (``attr.ib`` will *never* go away,` |
| `.venv-release-test/Lib/site-packages/attr/_make.py` | 1357 | `target_token` | `*never* go away, though).` |
| `.venv-release-test/Lib/site-packages/attr/_next_gen.py` | 340 | `target_token` | `Added *force_kw_only* to go back to the previous *kw_only* behavior.` |
| `.venv-release-test/Lib/site-packages/click/_compat.py` | 393 | `target_token` | `# Non-atomic writes directly go out through the regular open functions.` |
| `.venv-release-test/Lib/site-packages/click/core.py` | 1089 | `target_token` | `"""Returns all the pieces that go into the usage line and returns` |
| `.venv-release-test/Lib/site-packages/click/core.py` | 1964 | `target_token` | `# resolve things like --help which now should go to the main` |
| `.venv-release-test/Lib/site-packages/click/parser.py` | 235 | `target_token` | `should go with.` |
| `.venv-release-test/Lib/site-packages/click/termui.py` | 732 | `target_token` | `depending on which one they go with.` |
| `.venv-release-test/Lib/site-packages/click/types.py` | 819 | `target_token` | `Files can also be opened atomically in which case all writes go into a` |
| `.venv-release-test/Lib/site-packages/dateutil/easter.py` | 44 | `target_token` | ``GM Arts: Easter Algorithms <http://www.gmarts.org/index.php?go=415>`_` |
| `.venv-release-test/Lib/site-packages/dateutil/parser/_parser.py` | 28 | `target_token` | `- `Java SimpleDateFormat Class` |
| `.venv-release-test/Lib/site-packages/dateutil/rrule.py` | 184 | `target_token` | `""" Returns the number of recurrences in this set. It will have go` |
| `.venv-release-test/Lib/site-packages/flet/core/control.py` | 405 | `target_token` | `# go through children` |
| `.venv-release-test/Lib/site-packages/flet/core/page.py` | 927 | `target_token` | `def go(` |
| `.venv-release-test/Lib/site-packages/flet/core/page.py` | 944 | `target_token` | `self.query()  # Update query url (required when using go)` |
| `.venv-release-test/Lib/site-packages/fontTools/cffLib/specializer.py` | 563 | `target_token` | `# 5. Combine adjacent operators when possible, minding not to go over max stack size.` |
| `.venv-release-test/Lib/site-packages/fontTools/cffLib/specializer.py` | 729 | `target_token` | `# 5. Combine adjacent operators when possible, minding not to go over max stack size.` |
| `.venv-release-test/Lib/site-packages/fontTools/cu2qu/cu2qu.py` | 499 | `target_token` | `# done. go home` |
| `.venv-release-test/Lib/site-packages/fontTools/cu2qu/cu2qu.py` | 566 | `target_token` | `# done. go home` |
| `.venv-release-test/Lib/site-packages/fontTools/merge/layout.py` | 313 | `target_token` | `return None  # Don't shoot the messenger; let it go` |
| `.venv-release-test/Lib/site-packages/fontTools/misc/bezierTools.py` | 1324 | `target_token` | `# If bounds don't intersect, go home` |
| `.venv-release-test/Lib/site-packages/fontTools/misc/filenames.py` | 186 | `target_token` | `# if there is a clash, go to the next fallback` |
| `.venv-release-test/Lib/site-packages/fontTools/subset/__init__.py` | 1211 | `target_token` | `return None  # Don't shoot the messenger; let it go` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/E_B_D_T_.py` | 103 | `target_token` | `# Go through the bitmap glyph data. Just in case the data for a glyph` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/E_B_D_T_.py` | 154 | `target_token` | `# For now if both metrics exist go with glyph metrics.` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/E_B_L_C_.py` | 47 | `target_token` | `# hori and vert go between the two parts.` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/ttProgram.py` | 552 | `target_token` | `>>> asm = ['SVTCA[0]']` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/ttProgram.py` | 553 | `target_token` | `>>> p.fromAssembly(asm)` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/ttProgram.py` | 587 | `target_token` | `asm = p.getAssembly(preserve=True)` |
| `.venv-release-test/Lib/site-packages/fontTools/ttLib/tables/ttProgram.py` | 588 | `target_token` | `p.fromAssembly(asm)` |
| `.venv-release-test/Lib/site-packages/fontTools/ufoLib/filenames.py` | 282 | `target_token` | `# if there is a clash, go to the next fallback` |
| `.venv-release-test/Lib/site-packages/fontTools/unicodedata/ScriptExtensions.py` | 275 | `target_token` | `0xA9CF,  # .. 0xA9CF ; {'Bugi', 'Java'}` |
| `.venv-release-test/Lib/site-packages/fontTools/unicodedata/ScriptExtensions.py` | 789 | `target_token` | `{"Bugi", "Java"},  # A9CF..A9CF` |
| `.venv-release-test/Lib/site-packages/fontTools/unicodedata/Scripts.py` | 2492 | `target_token` | `"Java",  # A980..A9CD ; Javanese` |
| `.venv-release-test/Lib/site-packages/fontTools/unicodedata/Scripts.py` | 2495 | `target_token` | `"Java",  # A9D0..A9D9 ; Javanese` |
| `.venv-release-test/Lib/site-packages/fontTools/unicodedata/Scripts.py` | 2497 | `target_token` | `"Java",  # A9DE..A9DF ; Javanese` |
| `.venv-release-test/Lib/site-packages/fontTools/unicodedata/Scripts.py` | 3524 | `target_token` | `"Java": "Javanese",` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/avar/unbuild.py` | 55 | `target_token` | `# No pin found. Go through the previous masters` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/cff.py` | 356 | `target_token` | `# a VarData table to go with, and set vsindex.` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/featureVars.py` | 312 | `target_token` | `# representable as a box, so return full bottom and go home.` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/featureVars.py` | 679 | `target_token` | `"""Go through the scripts list, and remap feature indices."""` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/hvar.py` | 16 | `target_token` | `# There's two ways we can go from here:` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/hvar.py` | 22 | `target_token` | `# We'll go with the second option, as it's simpler, faster, and more direct.` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/merger.py` | 706 | `target_token` | `# We can even go further and reclassify marks to support any` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/merger.py` | 1564 | `target_token` | `# Simply flush the final list of layers and go home.` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/mutator.py` | 375 | `target_token` | `asm = []` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/mutator.py` | 378 | `target_token` | `asm = fpgm.program.getAssembly()` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/mutator.py` | 390 | `target_token` | `fpgm.program.fromAssembly(asm)` |
| `.venv-release-test/Lib/site-packages/fontTools/varLib/varStore.py` | 672 | `target_token` | `# Recalculate things and go home.` |
| `.venv-release-test/Lib/site-packages/h11/_connection.py` | 271 | `target_token` | `# All events go through here` |
| `.venv-release-test/Lib/site-packages/h11/_state.py` | 64 | `target_token` | `#    process_client_switch_proposals), and they go from True->False when we` |
| `.venv-release-test/Lib/site-packages/h11/_state.py` | 329 | `target_token` | `# priority. From there the client will either go to` |
| `.venv-release-test/Lib/site-packages/h11/_state.py` | 332 | `target_token` | `# request, in which case the client will go back to DONE and then` |
| `.venv-release-test/Lib/site-packages/httpx/_utils.py` | 108 | `target_token` | `# Assuming so, go to end of stream to figure out its length,` |
| `.venv-release-test/Lib/site-packages/jsonschema/_format.py` | 287 | `target_token` | `# The built-in `idna` codec only implements RFC 3890, so we go elsewhere.` |
| `.venv-release-test/Lib/site-packages/jsonschema/_format.py` | 471 | `target_token` | `#       needs to go either into jsonpointer (pending` |
| `.venv-release-test/Lib/site-packages/jsonschema/tests/_suite.py` | 115 | `target_token` | `# We're doing crazy things, so if they go wrong, like a function` |
| `.venv-release-test/Lib/site-packages/matplotlib/_afm.py` | 5 | `target_token` | `complete than this, it was decided not to go with them because they were` |
| `.venv-release-test/Lib/site-packages/matplotlib/_api/__init__.py` | 386 | `target_token` | `# Go to Python's `site-packages` or `lib` from an editable install.` |
| `.venv-release-test/Lib/site-packages/matplotlib/_api/deprecation.py` | 103 | `target_token` | ```@deprecated`` decorator should go *under* ``@classmethod`` and` |
| `.venv-release-test/Lib/site-packages/matplotlib/_constrained_layout.py` | 397 | `target_token` | `# make margin for colorbars.  These margins go in the` |
| `.venv-release-test/Lib/site-packages/matplotlib/axes/_axes.py` | 46 | `target_token` | `# All the other methods should go in the _AxesBase class.` |
| `.venv-release-test/Lib/site-packages/matplotlib/axes/_axes.py` | 1585 | `target_token` | `>>> plot(x2, y2, 'go')` |
| `.venv-release-test/Lib/site-packages/matplotlib/axes/_axes.py` | 5300 | `target_token` | `# flat indices, plus one so that out-of-range points go to position 0.` |
| `.venv-release-test/Lib/site-packages/matplotlib/axis.py` | 1355 | `target_token` | `# go back to just this axis's tick labels` |
| `.venv-release-test/Lib/site-packages/matplotlib/backend_bases.py` | 1048 | `target_token` | `# Set .interval and not ._interval to go through the property setter.` |
| `.venv-release-test/Lib/site-packages/matplotlib/backend_bases.py` | 2999 | `target_token` | `# go through zorders in reverse until we hit a capturing axes` |
| `.venv-release-test/Lib/site-packages/matplotlib/backends/backend_ps.py` | 341 | `target_token` | `go = font.getGlyphOrder()` |
| `.venv-release-test/Lib/site-packages/matplotlib/backends/backend_ps.py` | 342 | `target_token` | `s = f'/CharStrings {len(go)} dict dup begin\n'` |
| `.venv-release-test/Lib/site-packages/matplotlib/backends/backend_ps.py` | 343 | `target_token` | `for i, name in enumerate(go):` |
| `.venv-release-test/Lib/site-packages/matplotlib/backends/backend_svg.py` | 1026 | `target_token` | `# x64 to go back to FreeType's internal (integral) units.` |
| `.venv-release-test/Lib/site-packages/matplotlib/cbook.py` | 751 | `target_token` | `# Don't go back through the original list of objects, or` |
| `.venv-release-test/Lib/site-packages/matplotlib/collections.py` | 1455 | `target_token` | `# Handle scalar f2 (e.g. 0): the fill should go all` |
| `.venv-release-test/Lib/site-packages/matplotlib/colors.py` | 2790 | `target_token` | `go to infinity around zero).` |

## Nota de uso

Este inventario es exclusivamente histórico/diagnóstico. No implica soporte vigente para estos targets retirados.
