export function ordenar(lista) {
    return [...lista].sort();
}

export function maximo(lista) {
    return Math.max(...lista);
}

export function minimo(lista) {
    return Math.min(...lista);
}

export function sin_duplicados(lista) {
    return Array.from(new Set(lista));
}
