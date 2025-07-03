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

## Gramática de resaltado

La extensión incluye una gramática TextMate (`syntaxes/cobra.tmLanguage.json`) que define palabras clave, cadenas, números y comentarios de Cobra. Existe además un archivo `language-configuration.json` con las reglas de comentarios y parejas de llaves.

Para ajustar los colores, puedes editar tu `settings.json` y usar `editor.tokenColorCustomizations` con reglas `textMateRules` que apliquen al scope `source.cobra`.
