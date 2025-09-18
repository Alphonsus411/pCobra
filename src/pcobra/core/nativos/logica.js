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
