Cómo contribuir al proyecto
===========================

A continuación se describe el flujo habitual de contribución utilizando GitHub.

1. Realiza un *fork* del repositorio en tu cuenta.
2. Clona tu fork y crea una rama para cada cambio:

   .. code-block:: bash

      git clone https://github.com/TU_USUARIO/pCobra.git
      cd pCobra
      git checkout -b mi-rama

3. Aplica tus modificaciones y confirma los cambios con ``git commit``.
4. Sube la rama a tu fork:

   .. code-block:: bash

      git push origin mi-rama

5. Desde GitHub abre un *pull request* hacia la rama ``main`` del repositorio
   original explicando brevemente tus cambios.
6. Espera la revisión y realiza ajustes si es necesario.

Con este flujo mantenemos el código ordenado y es más sencillo revisar cada contribución.

Regeneración de política de targets (obligatorio al tocar docs/CLI)
--------------------------------------------------------------------

Cuando cambies la política de targets, el registro de transpiladores o documentación pública asociada, regenera todos los artefactos derivados con un único comando:

.. code-block:: bash

   python scripts/generate_target_policy_docs.py

Este comando sincroniza automáticamente:

* ``README.md`` (bloque normativo entre marcadores).
* ``docs/README.en.md`` (bloque normativo en inglés entre marcadores).
* ``docs/targets_policy.md`` (tiers, tabla de estado y separación runtime entre marcadores).
* ``docs/_generated/target_policy_summary.md``.
* ``docs/_generated/target_policy_summary.rst``.
* ``docs/_generated/target_policy_tiers.md``.
* ``docs/_generated/target_policy_status_table.md``.
* ``docs/_generated/target_policy_runtime_split.md``.
* ``docs/_generated/official_targets_table.rst``.
* ``docs/_generated/runtime_capability_matrix.rst``.
* ``docs/_generated/reverse_scope_table.rst``.
* ``docs/_generated/cli_backend_examples.rst``.

Lista oficial por tiers y política de soporte
----------------------------------------------

Cuando documentes o modifiques comandos de transpilación, usa siempre esta lista canónica:

- **Tier 1**: ``python``, ``rust``, ``javascript``, ``wasm``.
- **Tier 2**: ``go``, ``cpp``, ``java``, ``asm``.

Política operativa de soporte:

- Incidencias Tier 1: triage inicial <= 2 días hábiles.
- Incidencias Tier 2: triage inicial <= 5 días hábiles.
- Cualquier promoción/degradación entre tiers requiere RFC, plan de migración y actualización de changelog.

No deben reintroducirse ejemplos/snippets de targets retirados en documentación pública activa. Si hace falta contexto histórico, usar únicamente documentación histórica y enlazar la guía ``docs/migracion_targets_retirados.md``.
