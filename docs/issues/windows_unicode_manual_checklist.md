# Checklist manual Windows — Unicode en REPL

Objetivo: validar de forma reproducible que el REPL se mantiene estable en Windows ante entradas Unicode válidas e inválidas, tanto en modo interactivo como con `stdin` redirigido.

## Contrato de saneamiento en frontera (CLI)

Todo texto que cruce el boundary de entrada de la CLI/REPL **debe** pasar por
`sanitize_input` antes de validación, dispatch o persistencia en historial.

Puntos de referencia del contrato:

- `sanitize_input`: normaliza Unicode y reemplaza surrogates inválidos por `�`.
- `InteractiveCommand._run_repl_loop`: sanea cada línea antes de
  validación/comandos especiales/ejecución.
- `SafeFileHistory.append_string`: sanea antes de persistir en el historial.

Además, en modo debug (y mientras Python no se ejecute con `-O`) existen
aserciones ligeras en frontera para detectar tempranamente cualquier surrogate
aislado remanente.

## Preparación del entorno (una sola vez)

1. Abrir terminal en Windows (PowerShell recomendado).
2. Ir al directorio del proyecto.
3. Activar entorno virtual si aplica.
4. Lanzar el REPL de la herramienta/proyecto.

> Nota: en pasos de “pegado”, usar siempre **Ctrl+V** (o clic derecho) para evitar diferencias con escritura automática.

## Pasos reproducibles

### 1) Tecleo de emoji

- [ ] En el prompt del REPL, teclear manualmente un emoji válido, por ejemplo: `🚀`.
- [ ] Confirmar envío con Enter.

**Resultado esperado**

- [ ] El REPL sigue operativo (acepta siguiente comando/input).
- [ ] No hay excepción Unicode en pantalla.
- [ ] La entrada con emoji queda registrada en historial sin corrupción.

### 2) Pegado de texto multilenguaje

- [ ] Copiar y pegar en el REPL una línea con mezcla de scripts, por ejemplo:
  `Español: niño | Português: ação | 中文: 你好 | العربية: مرحبا | हिन्दी: नमस्ते | emoji: 😄`
- [ ] Confirmar envío con Enter.

**Resultado esperado**

- [ ] El REPL permanece estable.
- [ ] El contenido Unicode válido se preserva (sin pérdida ni sustituciones inesperadas).
- [ ] El historial se escribe correctamente y contiene los caracteres válidos.

### 3) Pegado con surrogate roto

- [ ] Preparar una cadena con surrogate huérfano (ejemplo conceptual: `\ud83d`).
- [ ] Pegar esa entrada en el REPL y enviar con Enter.

**Resultado esperado**

- [ ] No hay crash.
- [ ] El surrogate inválido se reemplaza por `�` de forma consistente.
- [ ] El REPL continúa aceptando entradas después del saneamiento.
- [ ] El historial se persiste sin fallar.

### 4) Ejecución con redirección de `stdin`

- [ ] Crear un archivo de entrada que combine:
  - una línea Unicode válida (por ejemplo con emoji y texto multilenguaje), y
  - una línea con surrogate inválido.
- [ ] Ejecutar la CLI con `stdin` redirigido desde ese archivo.

Ejemplo orientativo en PowerShell (adaptar comando de arranque a tu CLI):

```powershell
# 1) Línea válida
"hola 😄 | 你好 | مرحبا" | Out-File -Encoding utf8 .\tmp_unicode_input.txt

# 2) Línea con surrogate roto (literal de ejemplo para prueba manual)
"\ud83d" | Add-Content -Encoding utf8 .\tmp_unicode_input.txt

# 3) Ejecución con redirección
Get-Content .\tmp_unicode_input.txt | <COMANDO_CLI_REPL>
```

**Resultado esperado**

- [ ] Proceso estable durante toda la ejecución.
- [ ] Sin excepciones por Unicode/surrogates en runtime.
- [ ] Unicode válido preservado.
- [ ] Reemplazo consistente de inválidos por `�`.

## Criterios de aceptación

Se considera validado cuando se cumplen **todos** los puntos:

- [ ] REPL estable en todas las pruebas (sin cierres inesperados ni bloqueos).
- [ ] Historial escrito correctamente en todos los casos, sin crash.
- [ ] Preservación de Unicode válido (emoji y texto multilenguaje intactos).
- [ ] Reemplazo consistente de entradas inválidas por `�`.
- [ ] Cero errores tipo `surrogates not allowed`.
- [ ] Sin cambios en parser/AST/interpreter (la validación es de frontera de entrada e historial).
