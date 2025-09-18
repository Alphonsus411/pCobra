import fetch from 'node-fetch';
import * as querystring from 'querystring';
import { promises as fs } from 'fs';
import path from 'path';

const MAX_RESP_SIZE = 1024 * 1024;
const MAX_REDIRECTS = 5;

function obtenerHostsPermitidos() {
    const permitido = process.env.COBRA_HOST_WHITELIST;
    if (!permitido) {
        throw new Error('COBRA_HOST_WHITELIST no establecido');
    }
    const hosts = new Set(
        permitido
            .split(',')
            .map((h) => h.trim().toLowerCase())
            .filter((h) => h)
    );
    if (!hosts.size) {
        throw new Error('COBRA_HOST_WHITELIST vacío');
    }
    return hosts;
}

function validarEsquema(url) {
    if (!url.toLowerCase().startsWith('https://')) {
        throw new Error('Esquema de URL no soportado');
    }
}

function validarHost(url, hosts) {
    const hostname = new URL(url).hostname.toLowerCase();
    if (!hosts.has(hostname)) {
        throw new Error('Host no permitido');
    }
}

function resolverRedireccion(actual, destino, hosts) {
    if (!destino) {
        throw new Error('Redirección sin encabezado Location');
    }
    const nuevaUrl = new URL(destino, actual).toString();
    validarEsquema(nuevaUrl);
    validarHost(nuevaUrl, hosts);
    return nuevaUrl;
}

async function leerTextoRespuesta(res) {
    if (!res.body) {
        return '';
    }
    const partes = [];
    let total = 0;
    for await (const chunk of res.body) {
        const buffer = Buffer.from(chunk);
        total += buffer.length;
        if (total > MAX_RESP_SIZE) {
            throw new Error('Respuesta demasiado grande');
        }
        partes.push(buffer);
    }
    const charset = res.headers.get('content-type')?.match(/charset=([^;]+)/i);
    const encoding = charset ? charset[1] : 'utf-8';
    return Buffer.concat(partes).toString(encoding);
}

async function guardarEnArchivo(res, destino, crearPadres) {
    if (!res.body) {
        await fs.writeFile(destino, '');
        return destino;
    }
    if (crearPadres) {
        await fs.mkdir(path.dirname(destino), { recursive: true });
    }
    const handle = await fs.open(destino, 'w');
    let total = 0;
    try {
        for await (const chunk of res.body) {
            const buffer = Buffer.from(chunk);
            total += buffer.length;
            if (total > MAX_RESP_SIZE) {
                throw new Error('Respuesta demasiado grande');
            }
            await handle.write(buffer);
        }
    } catch (err) {
        await handle.close();
        await fs.unlink(destino).catch(() => {});
        throw err;
    }
    await handle.close();
    return destino;
}

async function realizarPeticion(metodo, urlInicial, opciones = {}) {
    const { datos = null, permitirRedirecciones = false, destino = null, crearPadres = true } = opciones;
    validarEsquema(urlInicial);
    const hosts = obtenerHostsPermitidos();
    let urlActual = urlInicial;
    let restantes = MAX_REDIRECTS;
    while (true) {
        validarHost(urlActual, hosts);
        const fetchOptions = { method: metodo, redirect: 'manual' };
        if (datos) {
            fetchOptions.body = querystring.stringify(datos);
            fetchOptions.headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            };
        }
        const res = await fetch(urlActual, fetchOptions);
        if (permitirRedirecciones && res.status >= 300 && res.status < 400) {
            if (restantes === 0) {
                res.body?.cancel?.();
                throw new Error('Demasiadas redirecciones');
            }
            const destinoHeader = res.headers.get('location');
            urlActual = resolverRedireccion(urlActual, destinoHeader, hosts);
            res.body?.cancel?.();
            restantes -= 1;
            continue;
        }
        if (!res.ok) {
            const textoError = await leerTextoRespuesta(res).catch(() => '');
            throw new Error(`Error HTTP ${res.status}: ${textoError}`.trim());
        }
        validarEsquema(res.url);
        validarHost(res.url, hosts);
        if (destino) {
            return await guardarEnArchivo(res, destino, crearPadres);
        }
        return await leerTextoRespuesta(res);
    }
}

export async function obtener_url(url, permitirRedirecciones = false) {
    return await realizarPeticion('GET', url, { permitirRedirecciones });
}

export async function enviar_post(url, datos, permitirRedirecciones = false) {
    return await realizarPeticion('POST', url, {
        datos,
        permitirRedirecciones,
    });
}

export async function obtener_url_async(url, permitirRedirecciones = false) {
    return await obtener_url(url, permitirRedirecciones);
}

export async function enviar_post_async(url, datos, permitirRedirecciones = false) {
    return await enviar_post(url, datos, permitirRedirecciones);
}

export async function descargar_archivo(url, destino, opciones = {}) {
    const { permitirRedirecciones = false, crearPadres = true } = opciones;
    return await realizarPeticion('GET', url, {
        permitirRedirecciones,
        destino,
        crearPadres,
    });
}
