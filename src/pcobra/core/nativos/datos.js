function asegurarTabla(tabla) {
    if (!Array.isArray(tabla)) {
        throw new TypeError('Se esperaba una lista de registros (array de objetos).');
    }
    return tabla.map((fila) => {
        if (fila == null || typeof fila !== 'object' || Array.isArray(fila)) {
            throw new TypeError('Cada fila debe ser un objeto con pares clave-valor.');
        }
        return { ...fila };
    });
}

function normalizarColumnas(columnas) {
    if (columnas == null || typeof columnas !== 'object' || Array.isArray(columnas)) {
        throw new TypeError('Se esperaba un objeto columna -> valores.');
    }
    return columnas;
}

function errorNoDisponible(funcion) {
    return new Error(
        `${funcion} solo está disponible en el backend de Python con pandas. ` +
            'En JavaScript debes preparar los datos manualmente o trabajar con estructuras básicas.',
    );
}

export function leer_csv() {
    throw errorNoDisponible('leer_csv');
}

export function leer_json() {
    throw errorNoDisponible('leer_json');
}

export function describir() {
    throw errorNoDisponible('describir');
}

export function agrupar_y_resumir() {
    throw errorNoDisponible('agrupar_y_resumir');
}

export function seleccionar_columnas(tabla, columnas) {
    const datos = asegurarTabla(tabla);
    if (!Array.isArray(columnas)) {
        throw new TypeError('columnas debe ser una lista.');
    }
    columnas.forEach((columna) => {
        if (typeof columna !== 'string') {
            throw new TypeError('Cada nombre de columna debe ser una cadena.');
        }
    });
    return datos.map((fila) => {
        const resultado = {};
        columnas.forEach((columna) => {
            if (!(columna in fila)) {
                throw new Error(`La columna ${columna} no existe en al menos una fila.`);
            }
            resultado[columna] = fila[columna];
        });
        return resultado;
    });
}

export function filtrar(tabla, condicion) {
    const datos = asegurarTabla(tabla);
    if (typeof condicion !== 'function') {
        throw new TypeError('condicion debe ser una función.');
    }
    return datos.filter((fila) => {
        const resultado = condicion({ ...fila });
        return Boolean(resultado);
    });
}

export function a_listas(tabla) {
    const datos = asegurarTabla(tabla);
    const columnas = {};
    datos.forEach((fila) => {
        Object.keys(fila).forEach((columna) => {
            if (!columnas[columna]) {
                columnas[columna] = [];
            }
            columnas[columna].push(fila[columna]);
        });
    });
    return columnas;
}

export function de_listas(columnas) {
    const entradas = Object.entries(normalizarColumnas(columnas));
    if (entradas.length === 0) {
        return [];
    }
    const longitud = entradas[0][1].length;
    entradas.forEach(([nombre, valores]) => {
        if (!Array.isArray(valores)) {
            throw new TypeError(`Los valores de la columna ${nombre} deben ser una lista.`);
        }
        if (valores.length !== longitud) {
            throw new Error('Todas las columnas deben tener la misma longitud.');
        }
    });
    const filas = [];
    for (let i = 0; i < longitud; i += 1) {
        const fila = {};
        entradas.forEach(([nombre, valores]) => {
            fila[nombre] = valores[i];
        });
        filas.push(fila);
    }
    return filas;
}
