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
