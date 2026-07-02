from pcobra.cobra_installer.logger import BuildLogger, ProgressEvent


def test_build_logger_emite_eventos_con_niveles_y_callbacks() -> None:
    events: list[ProgressEvent] = []
    legacy: list[str] = []
    logger = BuildLogger(events.append, legacy_callback=legacy.append)

    logger.step(
        "Detectando proyecto", stage="deteccion_proyecto", step=1, total_steps=10
    )
    logger.info("Validación correcta", stage="validacion")
    logger.warning("Dependencia en caché", stage="descarga_cache_cobrahub")
    logger.error("PyInstaller falló", stage="ejecucion_pyinstaller")

    assert [event.level for event in events] == ["step", "info", "warning", "error"]
    assert [event.stage for event in events] == [
        "deteccion_proyecto",
        "validacion",
        "descarga_cache_cobrahub",
        "ejecucion_pyinstaller",
    ]
    assert legacy == [
        "Detectando proyecto",
        "Validación correcta",
        "Dependencia en caché",
        "PyInstaller falló",
    ]
    assert str(events[0]) == "[PASO 1/10] Detectando proyecto"
