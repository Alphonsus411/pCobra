function asegurarIterable(lista, nombre = 'lista') {
    if (lista == null || typeof lista[Symbol.iterator] !== 'function') {
        throw new TypeError(`${nombre} debe ser iterable`);
    }
    return Array.from(lista);
}

function asegurarFuncion(fn, nombre = 'funcion') {
    if (typeof fn !== 'function') {
        throw new TypeError(`${nombre} debe ser una función`);
    }
    return fn;
}

function obtenerAccesorClave(clave) {
    if (typeof clave === 'function') {
        return clave;
    }
    if (typeof clave === 'string') {
        return (valor) => {
            if (valor == null) {
                throw new TypeError('No se puede obtener la clave de un valor nulo');
            }
            if (typeof valor === 'object' && clave in valor) {
                return valor[clave];
            }
            throw new Error(`El atributo o clave '${clave}' no existe en ${JSON.stringify(valor)}`);
        };
    }
    throw new TypeError('clave debe ser una función o una cadena');
}

function crearGeneradorPseudoAleatorio(semilla) {
    let seed = Number.parseInt(semilla, 10);
    if (!Number.isFinite(seed)) {
        throw new TypeError('semilla debe ser un número entero');
    }
    seed %= 2147483647;
    if (seed <= 0) {
        seed += 2147483646;
    }
    return () => {
        seed = (seed * 16807) % 2147483647;
        return (seed - 1) / 2147483646;
    };
}

export function ordenar(lista) {
    return asegurarIterable(lista).slice().sort();
}

export function maximo(lista) {
    const elementos = asegurarIterable(lista);
    if (elementos.length === 0) {
        throw new Error('maximo() no acepta listas vacías');
    }
    return Math.max(...elementos);
}

export function minimo(lista) {
    const elementos = asegurarIterable(lista);
    if (elementos.length === 0) {
        throw new Error('minimo() no acepta listas vacías');
    }
    return Math.min(...elementos);
}

export function sin_duplicados(lista) {
    return Array.from(new Set(asegurarIterable(lista)));
}

export function mapear(lista, funcion) {
    const elementos = asegurarIterable(lista);
    const fn = asegurarFuncion(funcion);
    return elementos.map((valor) => fn(valor));
}

export function filtrar(lista, funcion) {
    const elementos = asegurarIterable(lista);
    const fn = asegurarFuncion(funcion);
    return elementos.filter((valor) => fn(valor));
}

export function reducir(lista, funcion, inicial = undefined) {
    const elementos = asegurarIterable(lista);
    const fn = asegurarFuncion(funcion);
    if (elementos.length === 0 && inicial === undefined) {
        throw new Error('reducir() necesita al menos un elemento o un valor inicial');
    }
    if (inicial === undefined) {
        return elementos.slice(1).reduce((acc, actual) => fn(acc, actual), elementos[0]);
    }
    return elementos.reduce((acc, actual) => fn(acc, actual), inicial);
}

export function encontrar(lista, funcion, predeterminado = null) {
    const elementos = asegurarIterable(lista);
    const fn = asegurarFuncion(funcion);
    const encontrado = elementos.find((valor) => fn(valor));
    return encontrado !== undefined ? encontrado : predeterminado;
}

export function aplanar(lista) {
    const elementos = asegurarIterable(lista);
    const resultado = [];
    for (const elemento of elementos) {
        if (Array.isArray(elemento)) {
            resultado.push(...elemento);
        } else {
            resultado.push(elemento);
        }
    }
    return resultado;
}

export function agrupar_por(lista, clave) {
    const elementos = asegurarIterable(lista);
    const accessor = obtenerAccesorClave(clave);
    const resultado = {};
    for (const elemento of elementos) {
        const llave = accessor(elemento);
        const llaveNormalizada = typeof llave === 'string' || typeof llave === 'symbol' ? llave : String(llave);
        if (!Object.prototype.hasOwnProperty.call(resultado, llaveNormalizada)) {
            resultado[llaveNormalizada] = [];
        }
        resultado[llaveNormalizada].push(elemento);
    }
    return resultado;
}

export function particionar(lista, funcion) {
    const elementos = asegurarIterable(lista);
    const fn = asegurarFuncion(funcion);
    const verdaderos = [];
    const falsos = [];
    for (const elemento of elementos) {
        if (fn(elemento)) {
            verdaderos.push(elemento);
        } else {
            falsos.push(elemento);
        }
    }
    return [verdaderos, falsos];
}

export function mezclar(lista, semilla = null) {
    const elementos = asegurarIterable(lista);
    const resultado = elementos.slice();
    const generador = semilla === null ? () => Math.random() : crearGeneradorPseudoAleatorio(semilla);
    for (let i = resultado.length - 1; i > 0; i -= 1) {
        const j = Math.floor(generador() * (i + 1));
        [resultado[i], resultado[j]] = [resultado[j], resultado[i]];
    }
    return resultado;
}

export function zip_listas(...listas) {
    if (listas.length === 0) {
        return [];
    }
    const arreglos = listas.map((lista, indice) => asegurarIterable(lista, `lista_${indice + 1}`));
    const minimo = Math.min(...arreglos.map((arreglo) => arreglo.length));
    const resultado = [];
    for (let i = 0; i < minimo; i += 1) {
        resultado.push(arreglos.map((arreglo) => arreglo[i]));
    }
    return resultado;
}

export function tomar(lista, cantidad) {
    if (!Number.isInteger(cantidad)) {
        throw new TypeError('cantidad debe ser un entero');
    }
    if (cantidad < 0) {
        throw new RangeError('cantidad debe ser positiva');
    }
    const elementos = asegurarIterable(lista);
    return elementos.slice(0, cantidad);
}
