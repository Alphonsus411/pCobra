import crypto from 'crypto';

export function hash_sha256(texto) {
    return crypto.createHash('sha256').update(texto).digest('hex');
}

// ``hash_md5`` se mantiene como alias a ``hash_sha256`` por compatibilidad.
export const hash_md5 = hash_sha256;

export function generar_uuid() {
    return crypto.randomUUID();
}
