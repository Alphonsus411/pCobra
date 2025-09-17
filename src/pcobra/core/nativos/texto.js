const FORMAS_NORMALIZACION = new Set(["NFC", "NFD", "NFKC", "NFKD"]);

function repetirRelleno(relleno, longitud) {
    if (relleno.length === 0) {
        throw new Error("relleno no puede ser una cadena vacía");
    }
    if (longitud <= 0) {
        return "";
    }
    const repeticiones = Math.ceil(longitud / relleno.length);
    return relleno.repeat(repeticiones).slice(0, longitud);
}

function esEspacio(caracter) {
    return /\s/u.test(caracter);
}

function quitarEspaciosCustom(texto, modo, caracteres) {
    if (caracteres === "") {
        return texto;
    }
    const conjunto = new Set(Array.from(caracteres));
    const glifos = Array.from(texto);
    let inicio = 0;
    let fin = glifos.length;
    if (modo === "ambos" || modo === "izquierda") {
        while (inicio < fin && conjunto.has(glifos[inicio])) {
            inicio += 1;
        }
    }
    if (modo === "ambos" || modo === "derecha") {
        while (fin > inicio && conjunto.has(glifos[fin - 1])) {
            fin -= 1;
        }
    }
    return glifos.slice(inicio, fin).join("");
}

function dividirEspacios(texto, maximo) {
    const limite = maximo == null || maximo < 0 ? null : maximo;
    const resultado = [];
    let i = 0;
    let splits = 0;
    while (i < texto.length) {
        while (i < texto.length && esEspacio(texto[i])) {
            i += 1;
        }
        if (i >= texto.length) {
            break;
        }
        if (limite !== null && splits >= limite) {
            const resto = texto.slice(i).replace(/^\s+/u, "");
            resultado.push(resto);
            return resultado;
        }
        let inicio = i;
        while (i < texto.length && !esEspacio(texto[i])) {
            i += 1;
        }
        resultado.push(texto.slice(inicio, i));
        splits += 1;
    }
    return resultado;
}

function dividirConSeparador(texto, separador, maximo) {
    if (separador === "") {
        throw new Error("separador no puede ser una cadena vacía");
    }
    const limite = maximo == null || maximo < 0 ? null : maximo;
    if (limite === 0) {
        return [texto];
    }
    const partes = [];
    let inicio = 0;
    let splits = 0;
    while (inicio <= texto.length) {
        if (limite !== null && splits >= limite) {
            break;
        }
        const indice = texto.indexOf(separador, inicio);
        if (indice === -1) {
            break;
        }
        partes.push(texto.slice(inicio, indice));
        inicio = indice + separador.length;
        splits += 1;
    }
    partes.push(texto.slice(inicio));
    return partes;
}

export function mayusculas(texto) {
    return texto.toLocaleUpperCase();
}

export function minusculas(texto) {
    return texto.toLocaleLowerCase();
}

export function capitalizar(texto) {
    if (texto.length === 0) {
        return texto;
    }
    const primero = texto[0].toLocaleUpperCase();
    const resto = texto.slice(1).toLocaleLowerCase();
    return `${primero}${resto}`;
}

export function titulo(texto) {
    return texto
        .toLocaleLowerCase()
        .replace(/(^|\s)(\S)/gu, (coincidencia, separador, letra) => {
            return `${separador}${letra.toLocaleUpperCase()}`;
        });
}

export function invertir(texto) {
    return Array.from(texto).reverse().join("");
}

export function concatenar(...cadenas) {
    return cadenas.join("");
}

export function quitar_espacios(texto, modo = "ambos", caracteres = null) {
    if (!["ambos", "izquierda", "derecha"].includes(modo)) {
        throw new Error("modo debe ser 'ambos', 'izquierda' o 'derecha'");
    }
    if (caracteres == null) {
        if (modo === "ambos") {
            return texto.trim();
        }
        if (modo === "izquierda") {
            return texto.trimStart();
        }
        return texto.trimEnd();
    }
    return quitarEspaciosCustom(texto, modo, caracteres);
}

export function dividir(texto, separador = null, maximo = null) {
    if (separador == null) {
        return dividirEspacios(texto, maximo);
    }
    return dividirConSeparador(texto, separador, maximo);
}

export function unir(separador, piezas) {
    return Array.from(piezas, (parte) => String(parte)).join(separador);
}

export function reemplazar(texto, antiguo, nuevo, conteo = null) {
    const limite = conteo == null || conteo < 0 ? Number.POSITIVE_INFINITY : conteo;
    if (limite === 0) {
        return texto;
    }
    if (antiguo === "") {
        const maxReemplazos = Math.min(limite, texto.length + 1);
        if (maxReemplazos === 0) {
            return texto;
        }
        let resultado = "";
        let realizados = 0;
        for (const caracter of texto) {
            if (realizados < maxReemplazos) {
                resultado += nuevo;
                realizados += 1;
            }
            resultado += caracter;
        }
        if (realizados < maxReemplazos) {
            resultado += nuevo;
        }
        return resultado;
    }
    let resultado = "";
    let inicio = 0;
    let realizados = 0;
    while (inicio <= texto.length) {
        if (realizados >= limite) {
            break;
        }
        const indice = texto.indexOf(antiguo, inicio);
        if (indice === -1) {
            break;
        }
        resultado += texto.slice(inicio, indice) + nuevo;
        inicio = indice + antiguo.length;
        realizados += 1;
    }
    resultado += texto.slice(inicio);
    return resultado;
}

function comienzaCon(texto, prefijos) {
    if (typeof prefijos === "string") {
        return texto.startsWith(prefijos);
    }
    if (Array.isArray(prefijos) || prefijos instanceof Set) {
        for (const prefijo of prefijos) {
            if (texto.startsWith(prefijo)) {
                return true;
            }
        }
        return false;
    }
    return texto.startsWith(String(prefijos));
}

function terminaCon(texto, sufijos) {
    if (typeof sufijos === "string") {
        return texto.endsWith(sufijos);
    }
    if (Array.isArray(sufijos) || sufijos instanceof Set) {
        for (const sufijo of sufijos) {
            if (texto.endsWith(sufijo)) {
                return true;
            }
        }
        return false;
    }
    return texto.endsWith(String(sufijos));
}

export function empieza_con(texto, prefijos) {
    return comienzaCon(texto, prefijos);
}

export function termina_con(texto, sufijos) {
    return terminaCon(texto, sufijos);
}

export function incluye(texto, subcadena) {
    return texto.includes(subcadena);
}

export function rellenar_izquierda(texto, ancho, relleno = " ") {
    if (ancho <= texto.length) {
        return texto;
    }
    return repetirRelleno(relleno, ancho - texto.length) + texto;
}

export function rellenar_derecha(texto, ancho, relleno = " ") {
    if (ancho <= texto.length) {
        return texto;
    }
    return texto + repetirRelleno(relleno, ancho - texto.length);
}

export function normalizar_unicode(texto, forma = "NFC") {
    if (!FORMAS_NORMALIZACION.has(forma)) {
        throw new Error("forma debe ser una de NFC, NFD, NFKC o NFKD");
    }
    return texto.normalize(forma);
}
