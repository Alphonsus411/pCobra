export function es_par(n) {
    return n % 2 === 0;
}

export function es_primo(n) {
    if (n <= 1) return false;
    for (let i = 2; i <= Math.sqrt(n); i++) {
        if (n % i === 0) return false;
    }
    return true;
}

export function factorial(n) {
    let r = 1;
    for (let i = 1; i <= n; i++) {
        r *= i;
    }
    return r;
}

export function promedio(lista) {
    if (lista.length === 0) return 0;
    const total = lista.reduce((a, b) => a + b, 0);
    return total / lista.length;
}
