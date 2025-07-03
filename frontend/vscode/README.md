# Extensión Cobra para VS Code

Este directorio contiene una plantilla mínima de extensión que habilita el resaltado básico para archivos `.co`.

## Instalación de dependencias

```bash
cd frontend/vscode
npm install
```

## Ejecución de la extensión

1. Abre VS Code y carga este directorio como espacio de trabajo.
2. Pulsa `F5` para iniciar un "Extension Development Host".
3. En la nueva ventana, ejecuta el comando **Iniciar Cobra LSP** desde la paleta (`Ctrl+Shift+P`).
4. Para ejecutar el archivo Cobra actualmente abierto, presiona `Ctrl+R` o ejecuta el comando **Ejecutar archivo Cobra**.

El servidor de lenguaje se ejecutará mediante `python -m lsp.server` y proporcionará autocompletado y errores en vivo para archivos Cobra.

## Snippets incluidos

La extensión registra fragmentos de código (snippets) para acelerar la escritura.

- **func** &rarr; definición de función

```cobra
func nombre(parametros):
    
fin
```

- **si** &rarr; bloque condicional `si`/`sino`

```cobra
si condicion:
    
sino:
    
fin
```

- **para** &rarr; bucle `para`

```cobra
para item en iterable:
    
fin
```

Al escribir los prefijos anteriores y pulsar `Tab`, VS Code mostrará las plantillas correspondientes.

## Ejecutar scripts Cobra

Con la extensión activa puedes ejecutar rápidamente el archivo abierto con `Ctrl+R`. Esto lanzará `cobra ejecutar <archivo>` y mostrará la salida en el panel **Cobra**.

## Gramática de resaltado

La extensión incluye una gramática TextMate (`syntaxes/cobra.tmLanguage.json`) que define palabras clave, cadenas, números y comentarios de Cobra. Existe además un archivo `language-configuration.json` con las reglas de comentarios y parejas de llaves.

Para ajustar los colores, puedes editar tu `settings.json` y usar `editor.tokenColorCustomizations` con reglas `textMateRules` que apliquen al scope `source.cobra`.

## Pruebas manuales

Sigue estos pasos para comprobar que el servidor LSP ofrece sugerencias de Cobra:

1. Inicia la extensión con `F5` y ejecuta el comando **Iniciar Cobra LSP**.
2. Crea o abre un archivo con la extensión `.co`.
3. Al escribir prefijos como `func`, `si` o `cabeza` deberás ver en VS Code las
   sugerencias proporcionadas por el servidor.
