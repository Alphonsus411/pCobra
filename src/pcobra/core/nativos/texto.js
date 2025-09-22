const FORMAS_NORMALIZACION = new Set(["NFC", "NFD", "NFKC", "NFKD"]);
const PATRON_LETRAS = /^\p{Letter}+$/u;
const PATRON_ALFANUMERICO = /^[\p{Letter}\p{Number}]+$/u;
const PATRON_DECIMAL = /^\p{Decimal_Number}+$/u;
const PATRON_NUMERICO = /^\p{Number}+$/u;
const PATRON_ESPACIOS = /^\p{White_Space}+$/u;
const PATRON_IDENTIFICADOR_INICIO = /^[\p{ID_Start}_]$/u;
const PATRON_IDENTIFICADOR_CONTINUA = /^[\p{ID_Continue}_]$/u;
const REGEX_CONTROLES = /[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}]/u;
const REGEX_ESPACIOS = /\p{White_Space}/u;
const REGEX_SOLO_ESPACIOS = /^[ \t]+$/gm;
const REGEX_INDENTACION = /(^[ \t]*)(?:[^ \t\n])/gm;

const SIN_VALOR = Symbol("sin_valor");

function asegurarEntero(nombre, valor) {
    if (typeof valor === "boolean") {
        return valor ? 1 : 0;
    }
    if (typeof valor !== "number" || !Number.isInteger(valor)) {
        throw new TypeError(`${nombre} debe ser un entero`);
    }
    return valor;
}

function asegurarEnteroOpcional(nombre, valor) {
    if (valor == null) {
        return null;
    }
    return asegurarEntero(nombre, valor);
}

function ajustarRango(longitud, inicio, fin) {
    let inicioReal = inicio;
    let finReal = fin == null ? longitud : fin;
    if (inicioReal < 0) {
        inicioReal += longitud;
        if (inicioReal < 0) {
            inicioReal = 0;
        }
    } else if (inicioReal > longitud) {
        inicioReal = longitud;
    }
    if (fin == null) {
        finReal = longitud;
    } else {
        if (finReal < 0) {
            finReal += longitud;
        }
        if (finReal < 0) {
            finReal = 0;
        } else if (finReal > longitud) {
            finReal = longitud;
        }
    }
    if (finReal < inicioReal) {
        finReal = inicioReal;
    }
    return { inicio: inicioReal, fin: finReal };
}

function procesarPlantilla(formato, obtenerValor) {
    let resultado = "";
    let indiceAuto = 0;
    for (let i = 0; i < formato.length; ) {
        const caracter = formato[i];
        if (caracter === "{") {
            if (i + 1 < formato.length && formato[i + 1] === "{") {
                resultado += "{";
                i += 2;
                continue;
            }
            const cierre = formato.indexOf("}", i + 1);
            if (cierre === -1) {
                throw new Error("faltan llaves de cierre en la plantilla");
            }
            const contenido = formato.slice(i + 1, cierre);
            const [campoCrudo] = contenido.split(":", 1);
            const campo = campoCrudo.trim();
            let valor;
            if (campo === "") {
                valor = obtenerValor({ tipo: "auto", indice: indiceAuto });
                indiceAuto += 1;
            } else if (/^\d+$/.test(campo)) {
                valor = obtenerValor({ tipo: "posicional", indice: Number.parseInt(campo, 10) });
            } else {
                valor = obtenerValor({ tipo: "nombrado", clave: campo });
            }
            resultado += String(valor);
            i = cierre + 1;
            continue;
        }
        if (caracter === "}" && i + 1 < formato.length && formato[i + 1] === "}") {
            resultado += "}";
            i += 2;
            continue;
        }
        if (caracter === "}") {
            throw new Error("llave de cierre sin escapar");
        }
        resultado += caracter;
        i += 1;
    }
    return resultado;
}

function obtenerCodigoClave(clave) {
    if (typeof clave === "number" && Number.isInteger(clave)) {
        return clave;
    }
    if (typeof clave === "string") {
        const caracteres = Array.from(clave);
        if (caracteres.length !== 1) {
            throw new Error("las claves deben ser enteros o una cadena de un carácter");
        }
        return caracteres[0].codePointAt(0);
    }
    throw new TypeError("las claves deben ser enteros o cadenas");
}

function normalizarValorTraduccion(valor) {
    if (valor == null) {
        return null;
    }
    if (typeof valor === "number" && Number.isInteger(valor)) {
        return String.fromCodePoint(valor);
    }
    if (typeof valor === "string") {
        return valor;
    }
    throw new TypeError("los valores deben ser cadenas, enteros o null");
}

function crearTablaDesdeMapa(mapeo) {
    const tabla = Object.create(null);
    const entradas = mapeo instanceof Map ? mapeo.entries() : Object.entries(mapeo);
    for (const [clave, valor] of entradas) {
        const codigo = obtenerCodigoClave(clave);
        tabla[codigo] = normalizarValorTraduccion(valor);
    }
    return tabla;
}

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

function normalizarOpcional(texto, forma) {
    if (forma == null) {
        return texto;
    }
    return normalizar_unicode(texto, forma);
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

function escaparExpresionRegular(texto) {
    return texto.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
}

function dividirPalabraPorLongitud(palabra, longitud) {
    if (longitud <= 0) {
        return [palabra];
    }
    const partes = [];
    let inicio = 0;
    while (inicio < palabra.length) {
        partes.push(palabra.slice(inicio, inicio + longitud));
        inicio += longitud;
    }
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

export function encontrar(texto, subcadena, inicio = 0, fin = null, opciones = {}) {
    if (typeof subcadena !== "string") {
        throw new TypeError("subcadena debe ser una cadena");
    }
    const inicioReal = asegurarEntero("inicio", inicio);
    const finReal = asegurarEnteroOpcional("fin", fin);
    const opcionesEfectivas = opciones == null ? {} : opciones;
    const tienePorDefecto = Object.prototype.hasOwnProperty.call(
        opcionesEfectivas,
        "por_defecto",
    );
    const { por_defecto: porDefecto = SIN_VALOR } = opcionesEfectivas;
    const { inicio: indiceInicio, fin: indiceFin } = ajustarRango(
        texto.length,
        inicioReal,
        finReal,
    );
    const segmento = texto.slice(indiceInicio, indiceFin);
    const posicionRelativa = segmento.indexOf(subcadena);
    if (posicionRelativa === -1) {
        return tienePorDefecto ? porDefecto : -1;
    }
    return indiceInicio + posicionRelativa;
}

export function encontrar_derecha(
    texto,
    subcadena,
    inicio = 0,
    fin = null,
    opciones = {},
) {
    if (typeof subcadena !== "string") {
        throw new TypeError("subcadena debe ser una cadena");
    }
    const inicioReal = asegurarEntero("inicio", inicio);
    const finReal = asegurarEnteroOpcional("fin", fin);
    const opcionesEfectivas = opciones == null ? {} : opciones;
    const tienePorDefecto = Object.prototype.hasOwnProperty.call(
        opcionesEfectivas,
        "por_defecto",
    );
    const { por_defecto: porDefecto = SIN_VALOR } = opcionesEfectivas;
    const { inicio: indiceInicio, fin: indiceFin } = ajustarRango(
        texto.length,
        inicioReal,
        finReal,
    );
    const segmento = texto.slice(indiceInicio, indiceFin);
    const posicionRelativa = segmento.lastIndexOf(subcadena);
    if (posicionRelativa === -1) {
        return tienePorDefecto ? porDefecto : -1;
    }
    return indiceInicio + posicionRelativa;
}

export function indice(texto, subcadena, inicio = 0, fin = null, opciones = {}) {
    const opcionesEfectivas = opciones == null ? {} : opciones;
    const tienePorDefecto = Object.prototype.hasOwnProperty.call(
        opcionesEfectivas,
        "por_defecto",
    );
    const { por_defecto: porDefecto = SIN_VALOR } = opcionesEfectivas;
    const posicion = encontrar(texto, subcadena, inicio, fin);
    if (posicion === -1) {
        if (tienePorDefecto) {
            return porDefecto;
        }
        throw new Error("subcadena no encontrada");
    }
    return posicion;
}

export function indice_derecha(texto, subcadena, inicio = 0, fin = null, opciones = {}) {
    const opcionesEfectivas = opciones == null ? {} : opciones;
    const tienePorDefecto = Object.prototype.hasOwnProperty.call(
        opcionesEfectivas,
        "por_defecto",
    );
    const { por_defecto: porDefecto = SIN_VALOR } = opcionesEfectivas;
    const posicion = encontrar_derecha(texto, subcadena, inicio, fin);
    if (posicion === -1) {
        if (tienePorDefecto) {
            return porDefecto;
        }
        throw new Error("subcadena no encontrada");
    }
    return posicion;
}

export function formatear(formato, ...args) {
    if (typeof formato !== "string") {
        throw new TypeError("formato debe ser una cadena");
    }
    return procesarPlantilla(formato, ({ tipo, indice, clave }) => {
        if (tipo === "auto" || tipo === "posicional") {
            if (indice >= args.length) {
                throw new Error("faltan argumentos posicionales");
            }
            return args[indice];
        }
        throw new Error("usa formatear_mapa para campos nombrados");
    });
}

export function formatear_mapa(formato, valores) {
    if (typeof formato !== "string") {
        throw new TypeError("formato debe ser una cadena");
    }
    if (valores == null || typeof valores !== "object") {
        throw new TypeError("valores debe ser un mapeo");
    }
    const mapa = valores instanceof Map ? valores : new Map(Object.entries(valores));
    return procesarPlantilla(formato, ({ tipo, clave }) => {
        if (tipo !== "nombrado") {
            throw new Error("solo se permiten claves nombradas en formatear_mapa");
        }
        if (!mapa.has(clave)) {
            throw new Error(`clave '${clave}' no encontrada`);
        }
        return mapa.get(clave);
    });
}

export function tabla_traduccion(...argumentos) {
    if (argumentos.length === 0) {
        throw new Error("tabla_traduccion requiere al menos un argumento");
    }
    if (argumentos.length === 1) {
        const mapeo = argumentos[0];
        if (mapeo == null || typeof mapeo !== "object") {
            throw new TypeError("mapeo debe ser un mapeo");
        }
        return crearTablaDesdeMapa(mapeo);
    }
    if (argumentos.length === 2 || argumentos.length === 3) {
        const [desde, hacia, eliminados = ""] = argumentos;
        if (typeof desde !== "string") {
            throw new TypeError("desde debe ser una cadena");
        }
        if (typeof hacia !== "string") {
            throw new TypeError("hacia debe ser una cadena");
        }
        if (typeof eliminados !== "string") {
            throw new TypeError("eliminados debe ser una cadena");
        }
        const origen = Array.from(desde);
        const destino = Array.from(hacia);
        if (origen.length !== destino.length) {
            throw new Error("desde y hacia deben tener la misma longitud");
        }
        const tabla = Object.create(null);
        for (let i = 0; i < origen.length; i += 1) {
            tabla[origen[i].codePointAt(0)] = destino[i];
        }
        for (const caracter of Array.from(eliminados)) {
            tabla[caracter.codePointAt(0)] = null;
        }
        return tabla;
    }
    throw new Error("tabla_traduccion acepta 1, 2 o 3 argumentos");
}

export function traducir(texto, tabla) {
    if (tabla == null || typeof tabla !== "object") {
        throw new TypeError("tabla debe ser un mapeo");
    }
    const esMapa = tabla instanceof Map;
    const resultado = [];
    for (const caracter of texto) {
        const codigo = caracter.codePointAt(0);
        let reemplazo;
        if (esMapa) {
            if (tabla.has(codigo)) {
                reemplazo = tabla.get(codigo);
            } else if (tabla.has(caracter)) {
                reemplazo = tabla.get(caracter);
            }
        } else if (Object.prototype.hasOwnProperty.call(tabla, codigo)) {
            reemplazo = tabla[codigo];
        } else if (Object.prototype.hasOwnProperty.call(tabla, caracter)) {
            reemplazo = tabla[caracter];
        }
        if (reemplazo === undefined) {
            resultado.push(caracter);
        } else if (reemplazo === null) {
            continue;
        } else if (typeof reemplazo === "string") {
            resultado.push(reemplazo);
        } else if (typeof reemplazo === "number" && Number.isInteger(reemplazo)) {
            resultado.push(String.fromCodePoint(reemplazo));
        } else {
            throw new TypeError(
                "las entradas de la tabla deben ser cadenas, enteros o null",
            );
        }
    }
    return resultado.join("");
}

export function indentar_texto(texto, prefijo, opciones = {}) {
    const { solo_lineas_no_vacias = false } = opciones;
    const patron = solo_lineas_no_vacias ? /^(?=.*\S)/gm : /^/gm;
    return texto.replace(patron, () => prefijo);
}

export function desindentar_texto(texto) {
    let resultado = texto.replace(REGEX_SOLO_ESPACIOS, "");
    let margen = null;
    let coincidencia;
    while ((coincidencia = REGEX_INDENTACION.exec(resultado)) !== null) {
        const indentacion = coincidencia[1];
        if (margen === null) {
            margen = indentacion;
        } else if (indentacion.startsWith(margen)) {
            continue;
        } else if (margen.startsWith(indentacion)) {
            margen = indentacion;
        } else {
            let i = 0;
            const limite = Math.min(margen.length, indentacion.length);
            while (i < limite && margen[i] === indentacion[i]) {
                i += 1;
            }
            margen = margen.slice(0, i);
        }
    }
    REGEX_INDENTACION.lastIndex = 0;
    if (margen && margen.length > 0) {
        const patron = new RegExp(`^${escaparExpresionRegular(margen)}`, "gm");
        resultado = resultado.replace(patron, "");
    }
    return resultado;
}

export function envolver_texto(
    texto,
    ancho = 70,
    opciones = {},
) {
    const {
        indentacion_inicial = "",
        indentacion_subsecuente = "",
        como_texto = false,
    } = opciones;
    if (ancho <= 0) {
        throw new Error("ancho debe ser mayor que cero");
    }
    const palabras = texto.trim().length
        ? texto.trim().split(/\s+/u)
        : [];
    if (palabras.length === 0) {
        return como_texto ? "" : [];
    }
    const cola = [...palabras];
    const lineas = [];
    let indentacionActual = indentacion_inicial;
    let longitudActual = indentacionActual.length;
    let palabrasLinea = [];

    const finalizarLinea = () => {
        if (palabrasLinea.length === 0) {
            return;
        }
        const contenido = palabrasLinea.join(" ");
        lineas.push(indentacionActual + contenido);
        indentacionActual = indentacion_subsecuente;
        palabrasLinea = [];
        longitudActual = indentacionActual.length;
    };

    while (cola.length > 0) {
        let palabra = cola.shift();
        const extra = palabrasLinea.length > 0 ? 1 : 0;
        const espacioDisponible = ancho - (longitudActual + extra);
        if (espacioDisponible > 0 && palabra.length > espacioDisponible) {
            const partes = dividirPalabraPorLongitud(palabra, espacioDisponible);
            if (partes.length > 1) {
                cola.unshift(...partes.slice(1));
            }
            palabra = partes[0];
        }
        const necesario = extra + palabra.length;
        if (longitudActual + necesario <= ancho || palabrasLinea.length === 0) {
            if (extra === 1) {
                longitudActual += 1;
            }
            palabrasLinea.push(palabra);
            longitudActual += palabra.length;
        } else {
            finalizarLinea();
            cola.unshift(palabra);
        }
    }

    finalizarLinea();
    return como_texto ? lineas.join("\n") : lineas;
}

export function acortar_texto(
    texto,
    ancho,
    opciones = {},
) {
    const { marcador = " [...]" } = opciones;
    if (ancho <= 0) {
        throw new Error("ancho debe ser mayor que cero");
    }
    const colapsado = texto.trim().length
        ? texto.trim().split(/\s+/u).join(" ")
        : "";
    if (colapsado.length <= ancho) {
        return colapsado;
    }
    const limite = ancho - marcador.length;
    if (limite < 1) {
        throw new Error("el marcador es demasiado largo para el ancho indicado");
    }
    const palabras = colapsado.split(" ");
    let resultado = "";
    for (const palabra of palabras) {
        const candidato = resultado ? `${resultado} ${palabra}` : palabra;
        if (candidato.length > limite) {
            break;
        }
        resultado = candidato;
    }
    if (!resultado) {
        return marcador.trim();
    }
    return `${resultado}${marcador}`;
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

export function prefijo_comun(texto, otro, opciones = {}) {
    const { ignorar_mayusculas = false, normalizar = null } = opciones;
    const baseTexto = normalizarOpcional(texto, normalizar);
    const baseOtro = normalizarOpcional(otro, normalizar);
    const compararTexto = ignorar_mayusculas
        ? baseTexto.toLocaleLowerCase()
        : baseTexto;
    const compararOtro = ignorar_mayusculas
        ? baseOtro.toLocaleLowerCase()
        : baseOtro;
    const limite = Math.min(compararTexto.length, compararOtro.length);
    let indice = 0;
    while (indice < limite && compararTexto[indice] === compararOtro[indice]) {
        indice += 1;
    }
    return baseTexto.slice(0, indice);
}

export function sufijo_comun(texto, otro, opciones = {}) {
    const { ignorar_mayusculas = false, normalizar = null } = opciones;
    const baseTexto = normalizarOpcional(texto, normalizar);
    const baseOtro = normalizarOpcional(otro, normalizar);
    const compararTexto = ignorar_mayusculas
        ? baseTexto.toLocaleLowerCase()
        : baseTexto;
    const compararOtro = ignorar_mayusculas
        ? baseOtro.toLocaleLowerCase()
        : baseOtro;
    const limite = Math.min(compararTexto.length, compararOtro.length);
    let indice = 0;
    while (
        indice < limite &&
        compararTexto[compararTexto.length - indice - 1] ===
            compararOtro[compararOtro.length - indice - 1]
    ) {
        indice += 1;
    }
    if (indice === 0) {
        return "";
    }
    return baseTexto.slice(baseTexto.length - indice);
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

export function es_alfabetico(texto) {
    return texto.length > 0 && PATRON_LETRAS.test(texto);
}

export function es_alfa_numerico(texto) {
    return texto.length > 0 && PATRON_ALFANUMERICO.test(texto);
}

export function es_decimal(texto) {
    return texto.length > 0 && PATRON_DECIMAL.test(texto);
}

export function es_numerico(texto) {
    return texto.length > 0 && PATRON_NUMERICO.test(texto);
}

export function es_identificador(texto) {
    if (texto.length === 0) {
        return false;
    }
    const caracteres = Array.from(texto);
    if (!PATRON_IDENTIFICADOR_INICIO.test(caracteres[0])) {
        return false;
    }
    for (let i = 1; i < caracteres.length; i += 1) {
        if (!PATRON_IDENTIFICADOR_CONTINUA.test(caracteres[i])) {
            return false;
        }
    }
    return true;
}

export function es_imprimible(texto) {
    for (const caracter of texto) {
        if (REGEX_CONTROLES.test(caracter)) {
            return false;
        }
        if (REGEX_ESPACIOS.test(caracter) && caracter !== " ") {
            return false;
        }
    }
    return true;
}

export function es_ascii(texto) {
    for (const caracter of texto) {
        if (caracter.codePointAt(0) > 0x7f) {
            return false;
        }
    }
    return true;
}

export function es_mayusculas(texto) {
    let tieneCased = false;
    for (const caracter of texto) {
        const mayuscula = caracter.toLocaleUpperCase();
        const minuscula = caracter.toLocaleLowerCase();
        if (mayuscula !== minuscula) {
            if (caracter !== mayuscula) {
                return false;
            }
            tieneCased = true;
        }
    }
    return tieneCased;
}

export function es_minusculas(texto) {
    let tieneCased = false;
    for (const caracter of texto) {
        const mayuscula = caracter.toLocaleUpperCase();
        const minuscula = caracter.toLocaleLowerCase();
        if (mayuscula !== minuscula) {
            if (caracter !== minuscula) {
                return false;
            }
            tieneCased = true;
        }
    }
    return tieneCased;
}

export function es_espacio(texto) {
    return texto.length > 0 && PATRON_ESPACIOS.test(texto);
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
