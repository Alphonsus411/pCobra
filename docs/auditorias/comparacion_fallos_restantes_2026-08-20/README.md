# Comparación nominal de los fallos restantes — 2026-08-20

## Alcance

Se tomó como baseline la sección «Fallos históricos restantes» de
`docs/auditorias/fix_usar_equivalencias_precedencia_2026-08-20/README.md`:
los casos 1–6 y 12–15 del triage original. La comparación se hizo por **node ID
completo**, no por el total agregado de fallos.

No se modificaron código, pruebas, Lexer ni Parser. Este documento registra la
comparación y trata la discrepancia nominal como un hallazgo independiente.

## Baseline nominal (10 nodos)

1. `tests/unit/test_holobit_no_fuga_exports.py::test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits]`
2. `tests/unit/test_holobit_no_fuga_exports.py::test_no_fuga_de_sdk_ni_clases_internas[pcobra.core.holobits-Holobit]`
3. `tests/unit/test_holobit_sdk_fallback_contract.py::test_gap_contract_non_python_declara_no_paridad_sdk`
4. `tests/unit/test_holobit_sdk_fallback_contract.py::test_fallback_contract_no_promueve_sdk_full_fuera_de_python[rust]`
5. `tests/unit/test_holobit_sdk_integration.py::test_graficar_usa_sdk`
6. `tests/unit/test_holobit_sdk_integration.py::test_python_es_el_unico_backend_con_sdk_full`
7. `tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co`
8. `tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink`
9. `tests/unit/test_usar_public_contract.py::test_usar_modulo_inexistente_falla_con_diagnostico_publico`
10. `tests/unit/test_usar_public_contract.py::test_rechaza_usar_ruta_backend_no_canonica_con_error_consistente`

## Nueva ejecución

Se volvió a ejecutar, en el orden documentado, la selección de 26 archivos de
`docs/auditoria_holobit_contract_fix.md`. El resultado fue:

```text
19 failed, 502 passed, 5 skipped, 2 warnings in 15.76s
```

Los node IDs completos extraídos del resumen fueron:

1. `tests/unit/test_holobit_no_fuga_exports.py::test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits]`
2. `tests/unit/test_holobit_no_fuga_exports.py::test_no_fuga_de_sdk_ni_clases_internas[pcobra.core.holobits-Holobit]`
3. `tests/unit/test_holobit_sdk_fallback_contract.py::test_gap_contract_non_python_declara_no_paridad_sdk`
4. `tests/unit/test_holobit_sdk_fallback_contract.py::test_fallback_contract_no_promueve_sdk_full_fuera_de_python[rust]`
5. `tests/unit/test_holobit_sdk_integration.py::test_graficar_usa_sdk`
6. `tests/unit/test_holobit_sdk_integration.py::test_python_es_el_unico_backend_con_sdk_full`
7. `tests/integration/test_repl_usar_entrypoints_contract.py::test_seguridad_usar_numpy_error_corto_sin_traceback_modo_normal`
8. `tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback[<lambda>-<lambda>]`
9. `tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback[ReplCommandV2-<lambda>]`
10. `tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_rechazo_numpy_es_persistente[<lambda>-<lambda>]`
11. `tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_rechazo_numpy_es_persistente[ReplCommandV2-<lambda>]`
12. `tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite`
13. `tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_usar_numpy_error_explicito_corto_sin_traceback_en_modo_normal`
14. `tests/integration/test_usar_core_contract_full.py::test_09_colision_reporta_error_estructurado`
15. `tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co`
16. `tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink`
17. `tests/unit/test_usar_numpy_error_contract.py::test_usar_numpy_rechaza_con_error_corto_sin_detalle_tecnico`
18. `tests/unit/test_usar_numpy_error_contract.py::test_usar_numpy_no_filtra_detalle_tecnico_en_log_normal`
19. `tests/unit/test_usar_numpy_error_contract.py::test_usar_numpy_incluye_detalle_tecnico_solo_con_debug`

## Diferencia de conjuntos

Sean `B` el baseline de diez nodos y `N` los diecinueve nodos de la nueva
ejecución:

- `B ∩ N` contiene **exactamente ocho** nodos: los seis fallos Holobit y los dos
  de `test_usar_loader_validation.py` enumerados como 1–8 en el baseline. Por
  tanto, los ocho supervivientes históricos sí son exclusivamente los
  solicitados.
- `B - N` contiene **exactamente dos** nodos:
  - caso 14,
    `tests/unit/test_usar_public_contract.py::test_usar_modulo_inexistente_falla_con_diagnostico_publico`;
  - caso 15,
    `tests/unit/test_usar_public_contract.py::test_rechaza_usar_ruta_backend_no_canonica_con_error_consistente`.
- `N - B` no está vacío: contiene los once nodos 7–14 y 17–19 de la lista de la
  nueva ejecución.

La desaparición dentro del baseline es, pues, exactamente la esperada para los
casos 14 y 15. Sin embargo, la ejecución global **no** tiene sólo ocho fallos:
aparecieron once nodos ajenos al baseline. En cumplimiento de la condición de
control, **no se documenta el cierre como satisfactorio**.

## Hallazgo independiente: once regresiones de contrato de mensajes

Los once nodos nuevos se concentran en dos cambios observables:

1. **Nueve fallos de diagnóstico de `numpy`.** La frontera pública devuelve
   ahora el texto corto prefijado por
   `usar_error[modulo_fuera_catalogo_publico]`. Las pruebas preexistentes
   esperan, según el punto de entrada, el diagnóstico de importación no
   permitida o el texto corto sin ese prefijo. También verifican que el prefijo
   no se filtre al log normal y que el detalle técnico sólo aparezca en modo
   debug.
2. **Dos fallos de colisión.** La traducción de cualquier `NameError` sustituye
   el mensaje original por `usar_error[conflicto_simbolo]`. Con ello se pierde
   el detalle estructurado de la colisión (`symbol_collision` y
   `colisión estructurada=...`) que ambos contratos todavía exigen.

La inspección de historial ubica ambas variaciones en el commit `e9eaa813`
(`Centraliza diagnósticos públicos de usar`): allí
`formatear_error_usar_usuario` empezó a anteponer códigos públicos,
`_error_usuario_modulo_fuera_catalogo` dejó de conservar sus variantes por
modo y `ejecutar_usar` empezó a reconstruir todo `NameError`. Esta atribución
explica los once nodos adicionales, pero no constituye una corrección: resolver
ese conflicto entre contratos debe hacerse incrementalmente en un hallazgo
separado.

## Conclusión

La comparación pedida arroja dos resultados distintos que no deben
confundirse:

- **Comparación histórica:** pasan sólo los casos 14 y 15, y sobreviven
  exactamente los ocho nodos indicados.
- **Estado de la suite:** no es satisfactorio, porque además existen once
  fallos nuevos de contratos de diagnóstico y colisión.

No se propone cerrar la auditoría hasta resolver o reconciliar explícitamente
ese hallazgo independiente.
