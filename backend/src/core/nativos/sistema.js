import os from 'os';
import fs from 'fs';
import child_process from 'child_process';

export function obtener_os() {
    return os.platform();
}

export function ejecutar(cmd) {
    return child_process.execSync(cmd, { encoding: 'utf-8' });
}

export function obtener_env(nombre) {
    return process.env[nombre];
}

export function listar_dir(ruta) {
    return fs.readdirSync(ruta);
}
