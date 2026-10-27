# Trazabilidad de reparación de benchmarks de CI

Estado a 2026-10-27. No sustituye los roadmaps ni autoriza fusiones.

## Referencias y dependencias

- `master` observado: `68e0465d3793078f2c7763f1e51f7748eb8e9f60`.
- [PR #3810](https://github.com/Alphonsus411/pCobra/pull/3810),
  `7e84531e8fbb3054299c99b5c1d24a24a4fadb48`: runner mediante el
  pipeline de backends. Abierta y en borrador; validación funcional incompleta.
- [PR #3812](https://github.com/Alphonsus411/pCobra/pull/3812),
  `f10586d20ea4cc85ca0396e2cdd975874c9e6b39`: rechaza procesos medidos
  con salida no nula. Apilada sobre #3810, abierta y en borrador.
- [PR #3811](https://github.com/Alphonsus411/pCobra/pull/3811),
  `fa2294270e71dfe2decd26075ba960d13fdf8187`: captura candidata de JSON.
  Apilada sobre #3810; aún no produce una baseline validada.
- `codex/benchmark-js-runtime-assets`: preparación de dependencias y módulos
  JavaScript del benchmark, pendiente de reconciliación y validación remota.

## Evidencia y límites

- #3810 dejó atrás el error de CLI `invalid choice: compilar`, pero el runner
  original ignoraba códigos de salida; no se certifica el benchmark completo.
- #3812 comprobó localmente ocho pruebas focales. El job de benchmark no se
  ejecutó en la PR apilada; sus checks no prueban el benchmark completo.
- El JavaScript generado en un directorio temporal falló al importar
  `nativos/io.js`. Al copiar los módulos, también faltó `node-fetch`.
- El bucle generado contiene `let x = x + 1` y Node reproduce un
  `ReferenceError`. Es una incidencia funcional separada; no se corrige aquí.
- Validación local adicional 2026-10-27 (Node 24): `var numero = 6` seguido de
  `imprimir(numero + 4)` falla en JavaScript por redeclaración del import
  `numero`; Python imprime `10`. La generación de `master` limpio
  `68e0465d3793078f2c7763f1e51f7748eb8e9f60` contiene el mismo conflicto.
  La prueba de regresión permanece local y fallida, no se ha desactivado.
- No hay baseline de release disponible: la última release y la rama
  `benchmarks-history` devolvieron 404 al diagnosticarlas.
- CodeQL pasó en las ejecuciones observadas; MyPy y el smoke Windows presentan
  fallos independientes. Los checks cancelados no cuentan como aprobados.

## Integración segura pendiente

1. Conciliar el entorno JavaScript con #3812 preservando su control de salida
   y pruebas; revisar el diff exacto y solapamientos con #3811.
2. Ejecutar pruebas focales y un programa Cobra real en Node 20, incluyendo
   dependencias ausentes y procesos fallidos; registrar SHA y resultados.
3. Abrir tarea funcional separada para la reasignación JavaScript. No modificar
   Lexer, Parser, AST, gramática ni sintaxis sin autorización específica.
4. Sólo con una medición válida, capturar y evaluar una baseline versionada;
   probar base presente, ausente, JSON inválido y comparación correcta.
5. Revisar PRs y checks por SHA, dependencias entre ramas, compatibilidad y
   protección de ramas antes de cualquier integración. No forzar fusiones ni
   omitir fallos. La captura de benchmark no demuestra por sí sola que la
   distribución pública del runtime JavaScript esté resuelta.

Actualizar este documento con evidencia fechada, hashes y enlaces al cerrar
cada tarea; no marcar como aprobada una comprobación omitida o pendiente.
