# Backlog técnico de equivalencia (autogenerado)

Fecha de generación: 2026-04-02
Versión contrato: 1.0.0

## Tareas abiertas (status != full)

- [ ] `decoradores` en `cpp` → elevar de `partial` a `full`. Contexto: Sin sintaxis nativa tipo @decorador.
- [ ] `decoradores` en `java` → elevar de `partial` a `full`. Contexto: Se transpila como anotación semántica en comentarios y wrappers.
- [ ] `decoradores` en `wasm` → elevar de `partial` a `full`. Contexto: Requiere soporte del host para instrumentación.
- [ ] `decoradores` en `asm` → elevar de `partial` a `full`. Contexto: Instrumentación manual, sin sintaxis declarativa.
- [ ] `imports_corelibs` en `javascript` → elevar de `partial` a `full`. Contexto: Cobertura parcial vía adaptadores del proyecto.
- [ ] `imports_corelibs` en `cpp` → elevar de `partial` a `full`. Contexto: Cobertura mínima orientada a utilidades base.
- [ ] `imports_corelibs` en `java` → elevar de `partial` a `full`. Contexto: APIs disponibles son un subconjunto del runtime Python.
- [ ] `imports_corelibs` en `wasm` → elevar de `partial` a `full`. Contexto: Depende completamente del host embebedor.
- [ ] `imports_corelibs` en `asm` → elevar de `partial` a `full`. Contexto: Runtime externo requerido para resolver llamadas.
- [ ] `manejo_errores` en `javascript` → elevar de `partial` a `full`. Contexto: Errores contractuales explícitos, semántica avanzada no cubierta.
- [ ] `manejo_errores` en `rust` → elevar de `partial` a `full`. Contexto: Basado en `Result`, no en excepciones.
- [ ] `manejo_errores` en `go` → elevar de `partial` a `full`. Contexto: Usa `panic/recover` para contratos no soportados.
- [ ] `manejo_errores` en `cpp` → elevar de `partial` a `full`. Contexto: Contrato centrado en `std::runtime_error`.
- [ ] `manejo_errores` en `java` → elevar de `partial` a `full`. Contexto: Usa `UnsupportedOperationException` para huecos funcionales.
- [ ] `manejo_errores` en `wasm` → elevar de `partial` a `full`. Contexto: Semántica de errores depende del host.
- [ ] `manejo_errores` en `asm` → elevar de `partial` a `full`. Contexto: Solo señalización de fallo; manejo externo.
- [ ] `async` en `cpp` → elevar de `none` a `full`. Contexto: Async no garantizado en el contrato actual.
- [ ] `async` en `java` → elevar de `none` a `full`. Contexto: Async no garantizado por el transpiler actual.
- [ ] `async` en `wasm` → elevar de `none` a `full`. Contexto: El módulo no garantiza await nativo.
- [ ] `async` en `asm` → elevar de `partial` a `full`. Contexto: Sin primitivas async nativas en backend.
- [ ] `tipos_compuestos` en `rust` → elevar de `partial` a `full`. Contexto: Conversión dinámica limitada frente a Python.
- [ ] `tipos_compuestos` en `go` → elevar de `partial` a `full`. Contexto: Tipado estático obliga coerciones explícitas.
- [ ] `tipos_compuestos` en `cpp` → elevar de `partial` a `full`. Contexto: Requiere wrappers para dinamismo tipo diccionario Python.
- [ ] `tipos_compuestos` en `java` → elevar de `partial` a `full`. Contexto: Conversión dinámica y genéricos limitan paridad.
- [ ] `tipos_compuestos` en `wasm` → elevar de `partial` a `full`. Contexto: Representación depende de ABI del host.
- [ ] `tipos_compuestos` en `asm` → elevar de `partial` a `full`. Contexto: Modelado manual de estructuras compuestas.

## Regla de mantenimiento

Ejecutar este script tras cualquier cambio en la matriz o backends para mantener el backlog sincronizado.
