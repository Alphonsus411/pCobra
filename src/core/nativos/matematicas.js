export function sumar(a, b) {
    return a + b;
}

export function promedio(lista) {
    if (lista.length === 0) return 0;
    const total = lista.reduce((a, b) => a + b, 0);
    return total / lista.length;
}

export function potencia(base, exponente) {
    return Math.pow(base, exponente);
}
