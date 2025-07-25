import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';

export function hash_md5(texto) {
    return crypto.createHash('md5').update(texto).digest('hex');
}

export function hash_sha256(texto) {
    return crypto.createHash('sha256').update(texto).digest('hex');
}

export function generar_uuid() {
    return uuidv4();
}
