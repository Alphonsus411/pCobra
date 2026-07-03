Empaquetar proyectos e instaladores
===================================

Flujo recomendado: Cobra Installer
----------------------------------

Para empaquetar un proyecto Cobra como ejecutable o carpeta distribuible usa el
subcomando público ``installer`` desde la raíz del proyecto:

.. code-block:: bash

   cobra installer build .
   cobra build --installer .

También puedes declarar el sistema operativo objetivo del artefacto:

.. code-block:: bash

   cobra installer build . --target windows
   cobra installer build . --target linux
   cobra installer build . --target macos

El proyecto debe tener un ``main.cobra`` en la raíz o un entrypoint configurado
en ``cobra.toml``. La guía completa está en :doc:`../cobra_installer`.

Uso desde el IDLE gráfico
-------------------------

El IDLE gráfico expone el botón **Empaquetar** para el proyecto activo:

1. Inicia ``cobra gui``.
2. Abre o crea un proyecto Cobra.
3. Pulsa **Empaquetar**.
4. Elige ``onedir`` o ``onefile``.
5. Confirma con **Empaquetar** y revisa el progreso en el panel de salida.

Si no hay proyecto o ruta activa, la interfaz debe avisar antes de construir. El
IDLE delega en ``pcobra.cobra_installer.idle_bridge`` y comparte la misma lógica
que la CLI.

OneDir y OneFile
----------------

``onedir`` es el modo predeterminado. Genera una carpeta en ``dist/`` con el
ejecutable, bibliotecas y recursos. Es más fácil de inspeccionar y depurar.

``onefile`` genera un único ejecutable. Es cómodo para distribución manual, pero
puede tardar más en arrancar porque PyInstaller extrae recursos en una ubicación
temporal.

Limitaciones de plataforma
--------------------------

PyInstaller debe construir normalmente en el mismo sistema operativo donde se
ejecutará el binario. La opción ``--target`` expresa la intención del build, pero
no convierte automáticamente Linux en un compilador nativo de Windows o macOS.
Para publicar artefactos multiplataforma usa:

- Docker para builds Linux reproducibles.
- VM Windows/macOS cuando necesites el sistema completo.
- CI con matriz ``windows``, ``linux`` y ``macos`` para releases.
- Builder remoto si el equipo local no tiene el SO, firma o dependencias.

Manifiesto de build
-------------------

Cada ejecución genera ``dist/cobra_build_manifest.json`` y, por compatibilidad,
``cobra-installer-manifest.json``. El manifiesto registra entrypoint, target,
modo ``onedir``/``onefile``, versiones de Cobra y PyInstaller, hashes SHA-256,
rutas de salida, recursos incluidos, dependencias y tamaño final. Adjunta este
archivo a los releases para auditoría y diagnóstico.

Errores comunes
---------------

- ``PyInstaller no disponible``: instala ``pyinstaller`` o ejecuta
  ``cobra installer build . --install-pyinstaller``.
- ``No se encontró entrypoint Cobra``: crea ``main.cobra`` o configura una única
  entrada en ``cobra.toml``.
- ``Permiso denegado``: cierra binarios previos, limpia ``build/`` y ``dist/`` y
  revisa antivirus/permisos.
- ``failed to execute script``: prueba ``--mode onedir`` y revisa imports o datos
  no incluidos.
- Build de otro sistema operativo: construye en ese SO mediante Docker, VM, CI o
  builder remoto.

Flujo histórico para empaquetar la CLI
--------------------------------------

El comando ``cobra empaquetar`` se mantiene para empaquetar la propia CLI de
Cobra como ejecutable independiente. Internamente ejecuta PyInstaller sobre la
CLI del proyecto.

.. code-block:: bash

   cobra empaquetar --output dist
   cobra empaquetar --name cobra --output dist

También puedes pasar un archivo ``.spec`` personalizado o incluir archivos
adicionales con ``--spec`` y ``--add-data``:

.. code-block:: bash

   cobra empaquetar --spec build/cobra.spec \
       --add-data "all-bytes.dat;all-bytes.dat" --output dist

Se necesita tener ``pyinstaller`` instalado previamente si no usas los flujos que
lo instalan explícitamente.
