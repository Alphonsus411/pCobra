# Limitaciones del sandbox de Node

Para ejecutar JavaScript de manera aislada Cobra utiliza Node y el módulo
`vm2`. La invocación se realiza con `--no-experimental-fetch` y un límite de
memoria `--max-old-space-size=128` para deshabilitar las capacidades de red
incluidas por defecto y restringir el consumo de memoria. El código se ejecuta
mediante `vm2` en un contexto vacío donde únicamente se expone un objeto
`console`. De esta forma no se tiene acceso a funciones internas de Node ni a
módulos del sistema. Además, la ejecución se realiza con un entorno de
variables reducido donde `PATH` apunta exclusivamente a `/usr/bin` o al
directorio que contiene el ejecutable de Node.

Es imprescindible mantener `vm2` actualizado; antes de cada ejecución se
verifica que la versión instalada sea al menos `3.9.19` para mitigar
vulnerabilidades conocidas.

Si la ejecución supera el tiempo límite configurado se aborta y se muestra un
mensaje de error. Estas restricciones buscan reducir la superficie de ataque al
ejecutar código de terceros.
