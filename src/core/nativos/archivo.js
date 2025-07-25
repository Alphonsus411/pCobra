import fs from 'fs';

export function leer(ruta) {
    return fs.readFileSync(ruta, 'utf-8');
}

export function escribir(ruta, datos) {
    fs.writeFileSync(ruta, datos);
}

export function existe(ruta) {
    return fs.existsSync(ruta);
}

export function eliminar(ruta) {
    if (fs.existsSync(ruta)) fs.unlinkSync(ruta);
}
