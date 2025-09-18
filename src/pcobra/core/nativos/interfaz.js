const NIVEL_A_ESTILO = {
    info: { icono: 'ℹ', estilo: '' },
    exito: { icono: '✔', estilo: '' },
    advertencia: { icono: '⚠', estilo: '' },
    error: { icono: '✖', estilo: '' },
};

export function mostrarTabla(filas, opciones = {}) {
    const { columnas = null, titulo = null } = opciones;
    if (titulo) {
        console.log(`\n=== ${titulo} ===`);
    }

    if (Array.isArray(filas) && columnas && columnas.length > 0) {
        const formateadas = filas.map((fila) => {
            if (fila && typeof fila === 'object' && !Array.isArray(fila)) {
                return columnas.reduce((acc, columna) => {
                    acc[columna] = fila[columna];
                    return acc;
                }, {});
            }
            if (Array.isArray(fila)) {
                return columnas.reduce((acc, columna, indice) => {
                    acc[columna] = fila[indice];
                    return acc;
                }, {});
            }
            return { valor: fila };
        });
        console.table(formateadas);
    } else {
        console.table(filas);
    }

    if (titulo) {
        console.log('');
    }
}

export function mostrarPanel(contenido, opciones = {}) {
    const { titulo = null } = opciones;
    const texto = Array.isArray(contenido) ? contenido.join('\n') : String(contenido);
    const lineas = texto.split('\n');
    const ancho = Math.max(...lineas.map((linea) => linea.length), titulo ? titulo.length + 2 : 0);
    const bordeHorizontal = '─'.repeat(ancho + 2);

    if (titulo) {
        const tituloCentrado = ` ${titulo} `;
        const restante = bordeHorizontal.length - tituloCentrado.length;
        const izquierda = Math.floor(restante / 2);
        const derecha = restante - izquierda;
        console.log(`┌${'─'.repeat(izquierda)}${tituloCentrado}${'─'.repeat(derecha)}┐`);
    } else {
        console.log(`┌${bordeHorizontal}┐`);
    }

    for (const linea of lineas) {
        const padding = ' '.repeat(ancho - linea.length);
        console.log(`│ ${linea}${padding} │`);
    }
    console.log(`└${bordeHorizontal}┘`);
}

export function limpiarConsola() {
    console.clear();
}

export function imprimirAviso(mensaje, opciones = {}) {
    const { nivel = 'info', icono = null } = opciones;
    const configuracion = NIVEL_A_ESTILO[nivel] || NIVEL_A_ESTILO.info;
    const simbolo = icono || configuracion.icono;
    console.log(`${simbolo} ${mensaje}`);
}

export function barraProgreso(total = null, opciones = {}) {
    const { descripcion = 'Progreso', stream = process.stdout } = opciones;
    let objetivo = typeof total === 'number' ? total : null;
    let completado = 0;
    let frame = 0;
    let finalizado = false;
    const spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

    const render = () => {
        if (finalizado) {
            return;
        }
        if (objetivo === null) {
            const simbolo = spinner[frame % spinner.length];
            frame += 1;
            stream.write(`\r${simbolo} ${descripcion} ${completado}`);
        } else {
            const porcentaje = objetivo === 0 ? 100 : Math.min(100, Math.round((completado / objetivo) * 100));
            const bloques = Math.round((porcentaje / 100) * 20);
            const barra = '█'.repeat(bloques) + '░'.repeat(20 - bloques);
            stream.write(`\r${descripcion} [${barra}] ${porcentaje}% (${completado}/${objetivo})`);
        }
    };

    const limpiarLinea = () => {
        stream.write('\r');
    };

    render();

    return {
        avanzar(cantidad = 1) {
            completado += cantidad;
            if (objetivo !== null) {
                completado = Math.min(completado, objetivo);
            }
            render();
        },
        actualizar(valor) {
            completado = valor;
            render();
        },
        completar() {
            finalizado = true;
            if (objetivo !== null) {
                completado = objetivo;
                render();
            }
            stream.write('\n');
        },
        reiniciar(nuevoTotal = objetivo) {
            objetivo = typeof nuevoTotal === 'number' ? nuevoTotal : null;
            completado = 0;
            finalizado = false;
            frame = 0;
            limpiarLinea();
            render();
        },
    };
}
