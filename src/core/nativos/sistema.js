import os

import 'child_process'
import 'fs'
import 'os'
import child_process
import fs

export function obtener_os() {
    return os.platform();
}

export function ejecutar(args, permitidos = null) {
    if (permitidos && args.length && !permitidos.includes(args[0])) {
        throw new Error(`Comando no permitido: ${args[0]}`);
    }
    const [program, ...rest] = args;
    const proc = child_process.spawnSync(program, rest, { encoding: 'utf-8' });
    if (proc.error) throw proc.error;
    if (proc.status !== 0) throw new Error(proc.stderr);
    return proc.stdout;
}

export function obtener_env(nombre) {
    return process.env[nombre];
}

export function listar_dir(ruta) {
    return fs.readdirSync(ruta);
}
