import fetch from 'node-fetch';
import * as querystring from 'querystring';

export async function obtener_url(url) {
    const res = await fetch(url);
    return await res.text();
}

export async function enviar_post(url, datos) {
    const res = await fetch(url, {
        method: 'POST',
        body: querystring.stringify(datos),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return await res.text();
}
