export function asegurarBooleano(valor, nombre = 'valor') {
    if (typeof valor === 'boolean') {
        return valor;
    }
    throw new TypeError(`${nombre} debe ser un booleano, se recibió ${typeof valor}`);
}

export function conjuncion(a, b) {
    const aBool = asegurarBooleano(a, 'a');
    const bBool = asegurarBooleano(b, 'b');
    return aBool && bBool;
}

export function disyuncion(a, b) {
    const aBool = asegurarBooleano(a, 'a');
    const bBool = asegurarBooleano(b, 'b');
    return aBool || bBool;
}

export function negacion(valor) {
    return !asegurarBooleano(valor);
}

export function xor(a, b) {
    return asegurarBooleano(a, 'a') !== asegurarBooleano(b, 'b');
}

export function nand(a, b) {
    return !conjuncion(a, b);
}

export function nor(a, b) {
    return !disyuncion(a, b);
}

export function implica(antecedente, consecuente) {
    return disyuncion(negacion(antecedente), consecuente);
}

export function equivale(a, b) {
    return !xor(a, b);
}

export function xorMultiple(...valores) {
    if (valores.length < 2) {
        throw new TypeError('xorMultiple requiere al menos dos valores booleanos');
    }
    return valores.reduce((resultado, valor, indice) => {
        const validado = asegurarBooleano(valor, `valor_${indice}`);
        return resultado !== validado;
    }, false);
}

export function todas(valores) {
    const lista = Array.from(valores);
    lista.forEach((valor, indice) => asegurarBooleano(valor, `valor_${indice}`));
    return lista.every((valor) => valor === true);
}

export function alguna(valores) {
    const lista = Array.from(valores);
    lista.forEach((valor, indice) => asegurarBooleano(valor, `valor_${indice}`));
    return lista.some((valor) => valor === true);
}

export function mayoria(valores) {
    const lista = Array.from(valores);
    if (lista.length === 0) {
        throw new Error('mayoria requiere al menos un valor booleano');
    }

    const verdaderos = lista.reduce((conteo, valor, indice) => {
        return conteo + (asegurarBooleano(valor, `valor_${indice}`) ? 1 : 0);
    }, 0);

    return verdaderos > lista.length / 2;
}

export function exactamenteN(valores, cantidad) {
    if (!Number.isInteger(cantidad)) {
        throw new TypeError(`cantidad debe ser un entero, se recibió ${typeof cantidad}`);
    }
    if (cantidad < 0) {
        throw new RangeError('cantidad no puede ser negativa en exactamenteN');
    }

    const lista = Array.from(valores);
    const verdaderos = lista.reduce((conteo, valor, indice) => {
        return conteo + (asegurarBooleano(valor, `valor_${indice}`) ? 1 : 0);
    }, 0);

    return verdaderos === cantidad;
}

function generarNombres(aridad, nombres) {
    if (nombres == null) {
        return Array.from({ length: aridad }, (_, indice) => `p${indice + 1}`);
    }

    const lista = Array.from(nombres);
    if (lista.length !== aridad) {
        throw new Error('La cantidad de nombres debe coincidir con la aridad');
    }
    return lista;
}

function resolverAridad(funcion, aridad) {
    if (aridad != null) {
        if (aridad < 0) {
            throw new RangeError('La aridad no puede ser negativa en tablaVerdad');
        }
        return aridad;
    }

    if (typeof funcion.length !== 'number') {
        throw new TypeError('No se pudo inferir la aridad de la función proporcionada');
    }

    return funcion.length;
}

function generarCombinaciones(aridad) {
    let combinaciones = [[]];
    for (let i = 0; i < aridad; i += 1) {
        const temporal = [];
        combinaciones.forEach((fila) => {
            temporal.push([...fila, false]);
            temporal.push([...fila, true]);
        });
        combinaciones = temporal;
    }
    return combinaciones;
}

export function tablaVerdad(funcion, opciones = {}) {
    const { aridad = null, nombres = null, nombreResultado = 'resultado' } = opciones;

    if (typeof funcion !== 'function') {
        throw new TypeError('funcion debe ser callable en tablaVerdad');
    }
    if (typeof nombreResultado !== 'string') {
        throw new TypeError('nombreResultado debe ser una cadena');
    }

    const aridadResuelta = resolverAridad(funcion, aridad);
    const nombresColumnas = generarNombres(aridadResuelta, nombres);
    const combinaciones = generarCombinaciones(aridadResuelta);

    return combinaciones.map((combinacion) => {
        const resultado = asegurarBooleano(funcion(...combinacion), 'resultado');
        const fila = {};
        combinacion.forEach((valor, indice) => {
            fila[nombresColumnas[indice]] = valor;
        });
        fila[nombreResultado] = resultado;
        return fila;
    });
}

export function diferenciaSimetrica(...colecciones) {
    if (colecciones.length === 0) {
        throw new Error('diferenciaSimetrica requiere al menos una colección');
    }

    const listas = colecciones.map((coleccion, indiceColeccion) => {
        const lista = Array.from(coleccion).map((valor, indiceValor) => {
            return asegurarBooleano(valor, `valor_${indiceColeccion}_${indiceValor}`);
        });
        return lista;
    });

    const longitudEsperada = listas[0].length;
    listas.forEach((lista) => {
        if (lista.length !== longitudEsperada) {
            throw new Error('Todas las colecciones deben tener la misma longitud');
        }
    });

    return listas[0].map((_, indiceValor) => {
        let acumulado = false;
        listas.forEach((lista) => {
            acumulado = acumulado !== lista[indiceValor];
        });
        return acumulado;
    });
}
