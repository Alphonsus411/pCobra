export function ahora() {
    return Date.now();
}

export function formatear(fecha, formato) {
    const d = new Date(fecha);
    return d.toISOString();
}

export function dormir(ms) {
    return new Promise(res => setTimeout(res, ms));
}
