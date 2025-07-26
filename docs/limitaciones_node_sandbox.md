# Limitaciones del sandbox de Node

Para ejecutar JavaScript de manera aislada Cobra utiliza Node y el módulo
`vm`. La invocación se realiza con `--no-experimental-fetch` para deshabilitar
las capacidades de red incluidas por defecto. El código se compila mediante
`vm.Script` y se ejecuta en un contexto vacío donde únicamente se expone un
objeto `console`. De esta forma no se tiene acceso a funciones internas de
Node ni a módulos del sistema.

Si la ejecución supera el tiempo límite configurado se aborta y se muestra un
mensaje de error. Estas restricciones buscan reducir la superficie de ataque al
ejecutar código de terceros.
