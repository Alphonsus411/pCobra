from smooth_criminal.memory import calcular_score

def formatear_tiempo(segundos: float) -> str:
    """
    Devuelve el tiempo con 6 decimales y 's' al final.
    Usa truncamiento para evitar redondeo.
    """
    trunc = int(segundos * 1_000_000) / 1_000_000
    return f"{trunc:.6f}s"

def export_filename(base: str = "smooth_export", ext: str = "csv") -> str:
    """
    Genera un nombre de archivo con timestamp.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{timestamp}.{ext}"
