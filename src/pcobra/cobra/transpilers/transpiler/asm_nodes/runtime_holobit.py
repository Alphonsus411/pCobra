def build_holobit_runtime_lines() -> list[str]:
    return [
        '; backend asm: runtime de inspección/diagnóstico, sin paridad SDK equivalente',
        'cobra_holobit:',
        "    ; Runtime Holobit ASM: backend de inspección; conserva la representación simbólica del holobit.",
        '    RET',
        'cobra_proyectar:',
        "    ; Runtime Holobit ASM: backend de inspección/diagnóstico; la proyección requiere runtime externo.",
        '    TRAP',
        'cobra_transformar:',
        "    ; Runtime Holobit ASM: backend de inspección/diagnóstico; la transformación requiere runtime externo.",
        '    TRAP',
        'cobra_graficar:',
        "    ; Runtime Holobit ASM: backend de inspección/diagnóstico; la visualización requiere runtime externo.",
        '    TRAP',
    ]
