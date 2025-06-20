import fs from 'fs';
import fetch from 'node-fetch';

export function leer_archivo(ruta) {
    return fs.readFileSync(ruta, 'utf-8');
}

export function escribir_archivo(ruta, datos) {
    fs.writeFileSync(ruta, datos);
}

export async function obtener_url(url) {
    const res = await fetch(url);
    return await res.text();
}
