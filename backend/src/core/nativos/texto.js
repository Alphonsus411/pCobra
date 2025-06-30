export function mayusculas(texto) {
    return texto.toUpperCase();
}

export function minusculas(texto) {
    return texto.toLowerCase();
}

export function invertir(texto) {
    return texto.split('').reverse().join('');
}

export function concatenar(...cadenas) {
    return cadenas.join('');
}
