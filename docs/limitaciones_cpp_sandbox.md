# Limitaciones del sandbox de C++

`compilar_en_sandbox_cpp` ejecuta el código dentro del contenedor Docker
`cobra-cpp-sandbox`. El contenedor se lanza con restricciones estrictas de
seguridad:

* Se ejecuta como el usuario `nobody` (`--user 65534:65534`).
* El sistema de archivos es de solo lectura (`--read-only`) y solo se permite
  un directorio temporal (`--tmpfs /tmp`).
* No se conceden capacidades adicionales (`--cap-drop=ALL`).
* No hay acceso a la red (`--network=none`) y se limitan procesos y memoria
  (`--pids-limit` y `--memory`).

Si la imagen no está disponible o Docker no está instalado se rechaza la
operación con un error indicando que el contenedor de C++ no puede usarse.
