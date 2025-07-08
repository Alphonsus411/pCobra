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
3. La extensión iniciará automáticamente el servidor LSP. Si lo prefieres puedes usar el comando **Iniciar Cobra LSP**.
4. Para ejecutar el archivo Cobra actualmente abierto, presiona `Ctrl+R` o ejecuta el comando **Ejecutar archivo Cobra**.
5. Formatea el documento con `Ctrl+Alt+F` o mediante `Shift+Alt+F`.

El servidor de lenguaje (`python -m lsp.server`) ofrece autocompletado, detección de errores de sintaxis y formateo para archivos Cobra.

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

1. Inicia la extensión con `F5`. El servidor LSP se iniciará automáticamente.
2. Crea o abre un archivo con la extensión `.co`.
3. Al escribir prefijos como `func`, `si` o `cabeza` deberás ver en VS Code las
   sugerencias proporcionadas por el servidor.

## Empaquetar y publicar

Instala `vsce` una vez de forma global y genera el archivo `.vsix` con:

```bash
npm install -g vsce
vsce package
```

Esto creará un paquete instalable localmente. Para publicarlo en el Marketplace
asegúrate de actualizar `package.json` (autor, repositorio y versión) y ejecuta:

```bash
vsce publish
```

Debes iniciar sesión previamente con `vsce login <publisher>`.
