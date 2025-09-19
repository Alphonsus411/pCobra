export function absoluto(n) {
    return Math.abs(n);
}


export function redondear(valor, ndigitos = null) {
    if (ndigitos === null || ndigitos === undefined) {
        return Math.round(valor);
    }
    const factor = Math.pow(10, ndigitos);
    return Math.round(valor * factor) / factor;
}


function _aNumero(nombre, valor) {
    if (typeof valor === "number") {
        return valor;
    }
    if (typeof valor === "boolean") {
        return valor ? 1 : 0;
    }
    if (valor != null) {
        const primitivo = valor.valueOf?.();
        if (typeof primitivo === "number") {
            return primitivo;
        }
    }
    throw new TypeError(`${nombre} solo acepta números reales`);
}

function _esSignoNegativo(valor) {
    return valor < 0 || (valor === 0 && Object.is(valor, -0));
}

export function piso(valor) {
    return Math.floor(valor);
}


export function techo(valor) {
    return Math.ceil(valor);
}


export function raiz(valor, indice = 2) {
    const indiceFloat = Number(indice);
    if (indiceFloat === 0) {
        throw new Error("El índice de la raíz no puede ser cero");
    }
    if (valor < 0) {
        if (Number.isInteger(indiceFloat)) {
            if (Math.abs(indiceFloat) % 2 === 0) {
                throw new Error("No se puede calcular la raíz par de un número negativo");
            }
        } else {
            throw new Error(
                "No se puede calcular la raíz de índice fraccionario de un número negativo",
            );
        }
    }
    const magnitud = Math.pow(Math.abs(valor), 1 / indiceFloat);
    return valor < 0 ? -magnitud : magnitud;
}


export function potencia(base, exponente) {
    return Math.pow(base, exponente);
}


export function clamp(valor, minimo, maximo) {
    if (minimo > maximo) {
        throw new Error("El mínimo no puede ser mayor que el máximo");
    }
    return Math.min(Math.max(valor, minimo), maximo);
}

export function interpolar(inicio, fin, factor) {
    const inicioNumero = _aNumero("interpolar", inicio);
    const finNumero = _aNumero("interpolar", fin);
    const factorNumero = _aNumero("interpolar", factor);

    if (
        Number.isNaN(inicioNumero)
        || Number.isNaN(finNumero)
        || Number.isNaN(factorNumero)
    ) {
        return Number.NaN;
    }

    if (!Number.isFinite(factorNumero)) {
        return factorNumero > 0 ? finNumero : inicioNumero;
    }
    if (factorNumero <= 0) {
        return inicioNumero;
    }
    if (factorNumero >= 1) {
        return finNumero;
    }

    return inicioNumero + (finNumero - inicioNumero) * factorNumero;
}

export function envolver_modular(valor, modulo) {
    const divisor = _aNumero("envolver_modular", modulo);
    if (divisor === 0) {
        throw new Error("El módulo no puede ser cero");
    }
    const numero = _aNumero("envolver_modular", valor);
    let resto = numero % divisor;

    if (
        (resto > 0 && divisor > 0)
        || (resto < 0 && divisor < 0)
    ) {
        return resto;
    }

    if (resto === 0) {
        return divisor < 0 || Object.is(divisor, -0) ? -0 : 0;
    }

    resto += divisor;
    if (resto === 0) {
        return divisor < 0 || Object.is(divisor, -0) ? -0 : 0;
    }
    return resto;
}

export function es_finito(valor) {
    const numero = _aNumero("es_finito", valor);
    return Number.isFinite(numero);
}

export function es_infinito(valor) {
    const numero = _aNumero("es_infinito", valor);
    return numero === Infinity || numero === -Infinity;
}

export function es_nan(valor) {
    const numero = _aNumero("es_nan", valor);
    return Number.isNaN(numero);
}

export function copiar_signo(magnitud, signo) {
    const magnitudNumero = _aNumero("copiar_signo", magnitud);
    const signoNumero = _aNumero("copiar_signo", signo);
    const negativo = _esSignoNegativo(signoNumero);
    const magnitudAbsoluta = Math.abs(magnitudNumero);
    return negativo ? -magnitudAbsoluta : magnitudAbsoluta;
}


export function aleatorio(inicio = 0, fin = 1) {
    if (inicio > fin) {
        throw new Error("El inicio no puede ser mayor que el fin");
    }
    return Math.random() * (fin - inicio) + inicio;
}


export function mediana(lista) {
    if (!lista || lista.length === 0) {
        throw new Error("No se puede calcular la mediana de una secuencia vacía");
    }
    const ordenada = [...lista].sort((a, b) => a - b);
    const mitad = Math.floor(ordenada.length / 2);
    if (ordenada.length % 2 === 0) {
        return (ordenada[mitad - 1] + ordenada[mitad]) / 2;
    }
    return ordenada[mitad];
}


export function moda(lista) {
    if (!lista || lista.length === 0) {
        throw new Error("No se puede calcular la moda de una secuencia vacía");
    }
    const frecuencias = new Map();
    let maxConteo = 0;
    let modaActual = lista[0];
    for (const valor of lista) {
        const conteo = (frecuencias.get(valor) ?? 0) + 1;
        frecuencias.set(valor, conteo);
        if (conteo > maxConteo) {
            maxConteo = conteo;
            modaActual = valor;
        }
    }
    return modaActual;
}


export function desviacion_estandar(lista, muestral = false) {
    if (!lista || lista.length === 0) {
        throw new Error(
            "No se puede calcular la desviación estándar de una secuencia vacía",
        );
    }
    if (muestral && lista.length < 2) {
        throw new Error("La desviación estándar muestral requiere al menos dos valores");
    }
    const promedio = lista.reduce((acc, val) => acc + val, 0) / lista.length;
    const sumaCuadrados = lista.reduce(
        (acc, val) => acc + Math.pow(val - promedio, 2),
        0,
    );
    const divisor = muestral && lista.length > 1 ? lista.length - 1 : lista.length;
    return Math.sqrt(sumaCuadrados / divisor);
}


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
