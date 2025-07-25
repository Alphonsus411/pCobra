import os from 'os';
import fs from 'fs';
import child_process from 'child_process';

export function obtener_os() {
    return os.platform();
}

export function ejecutar(cmd) {
    const args = cmd.match(/(?:[^\s"']+|"[^"]*"|'[^']*')+/g) || [];
    const program = args.shift();
    const proc = child_process.spawnSync(program, args, { encoding: 'utf-8' });
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
