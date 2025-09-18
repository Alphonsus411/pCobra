import os from 'os';
import child_process from 'child_process';
import fs from 'fs';
import path from 'path';

const WHITELIST_ENV = 'COBRA_EJECUTAR_PERMITIDOS';
const PERMITIDOS_FIJOS = process.env[WHITELIST_ENV]
    ? process.env[WHITELIST_ENV].split(path.delimiter)
    : [];

function normalizarRuta(ruta) {
    const real = fs.realpathSync(ruta);
    const normalizada = path.normalize(real);
    return process.platform === 'win32' ? normalizada.toLowerCase() : normalizada;
}

function obtenerPermitidos(permitidos) {
    let lista = permitidos;
    if (!lista) {
        if (PERMITIDOS_FIJOS.length) {
            lista = PERMITIDOS_FIJOS;
        } else {
            throw new Error('Se requiere lista blanca de comandos permitidos');
        }
    }
    const conjunto = new Set();
    for (const ruta of lista) {
        conjunto.add(normalizarRuta(ruta));
    }
    if (!conjunto.size) {
        throw new Error('Lista blanca de comandos vacía');
    }
    return conjunto;
}

function buscarEnPath(comando) {
    if (path.isAbsolute(comando)) {
        return comando;
    }
    const rutas = process.env.PATH ? process.env.PATH.split(path.delimiter) : [];
    for (const base of rutas) {
        const candidato = path.join(base, comando);
        try {
            const stats = fs.statSync(candidato);
            if (stats.isFile()) {
                return candidato;
            }
        } catch (err) {
            continue; // No existe o no es accesible.
        }
    }
    return null;
}

function resolverEjecutable(args, permitidos) {
    if (!args || !args.length) {
        throw new Error('Comando vacío');
    }
    const permitidosReales = obtenerPermitidos(permitidos);
    const comando = args[0];
    const rutaEncontrada = buscarEnPath(comando);
    if (!rutaEncontrada) {
        throw new Error(`Comando no permitido: ${comando}`);
    }
    const rutaReal = fs.realpathSync(rutaEncontrada);
    const rutaNormalizada = normalizarRuta(rutaReal);
    if (!permitidosReales.has(rutaNormalizada)) {
        throw new Error(`Comando no permitido: ${rutaReal}`);
    }
    const { ino } = fs.statSync(rutaReal);
    return { args, rutaReal, inode: ino ?? 0 };
}

function verificarInode(rutaReal, inodeInicial) {
    const { ino } = fs.statSync(rutaReal);
    if ((ino ?? 0) !== inodeInicial) {
        throw new Error('El ejecutable cambió durante la ejecución');
    }
}

function segundosAMilisegundos(timeout) {
    if (timeout === null || timeout === undefined) {
        return undefined;
    }
    return timeout * 1000;
}

export function obtener_os() {
    return os.platform();
}

export function ejecutar(args, permitidos = null, timeout = null) {
    const { args: comando, rutaReal, inode } = resolverEjecutable(args, permitidos);
    const [programa, ...resto] = comando;
    const proc = child_process.spawnSync(programa, resto, {
        encoding: 'utf-8',
        timeout: segundosAMilisegundos(timeout),
    });
    if (proc.error) throw proc.error;
    verificarInode(rutaReal, inode);
    if (proc.status && proc.status !== 0) {
        if (proc.stderr) {
            return proc.stderr;
        }
        throw new Error(`Error al ejecutar '${comando.join(' ')}': código ${proc.status}`);
    }
    return proc.stdout;
}

export async function ejecutar_async(args, permitidos = null, timeout = null) {
    const { args: comando, rutaReal, inode } = resolverEjecutable(args, permitidos);
    const [programa, ...resto] = comando;
    const proc = child_process.spawn(programa, resto, {
        stdio: ['ignore', 'pipe', 'pipe'],
    });
    proc.stdout.setEncoding('utf-8');
    proc.stderr.setEncoding('utf-8');
    const stdoutChunks = [];
    const stderrChunks = [];
    proc.stdout.on('data', (chunk) => stdoutChunks.push(chunk));
    proc.stderr.on('data', (chunk) => stderrChunks.push(chunk));
    let temporizador = null;
    let vencido = false;
    const timeoutMs = segundosAMilisegundos(timeout);
    if (timeoutMs !== undefined) {
        temporizador = setTimeout(() => {
            vencido = true;
            proc.kill();
        }, timeoutMs);
    }
    return await new Promise((resolve, reject) => {
        proc.once('error', (err) => {
            if (temporizador) clearTimeout(temporizador);
            reject(err);
        });
        proc.once('close', (code) => {
            if (temporizador) clearTimeout(temporizador);
            try {
                verificarInode(rutaReal, inode);
            } catch (err) {
                reject(err);
                return;
            }
            const stderrTexto = stderrChunks.join('');
            if (vencido) {
                if (stderrTexto) {
                    resolve(stderrTexto);
                } else {
                    reject(
                        new Error(
                            `Tiempo de espera agotado al ejecutar '${comando.join(' ')}'`
                        )
                    );
                }
                return;
            }
            if (code && code !== 0) {
                if (stderrTexto) {
                    resolve(stderrTexto);
                } else {
                    reject(
                        new Error(
                            `Error al ejecutar '${comando.join(' ')}': código ${code}`
                        )
                    );
                }
                return;
            }
            resolve(stdoutChunks.join(''));
        });
    });
}

export async function* ejecutar_stream(args, permitidos = null, timeout = null) {
    const { args: comando, rutaReal, inode } = resolverEjecutable(args, permitidos);
    const [programa, ...resto] = comando;
    const proc = child_process.spawn(programa, resto, {
        stdio: ['ignore', 'pipe', 'pipe'],
    });
    proc.stdout.setEncoding('utf-8');
    proc.stderr.setEncoding('utf-8');
    const stderrChunks = [];
    proc.stderr.on('data', (chunk) => stderrChunks.push(chunk));
    let temporizador = null;
    let vencido = false;
    const timeoutMs = segundosAMilisegundos(timeout);
    if (timeoutMs !== undefined) {
        temporizador = setTimeout(() => {
            vencido = true;
            proc.kill();
        }, timeoutMs);
    }
    try {
        for await (const chunk of proc.stdout) {
            yield chunk;
        }
        await new Promise((resolve, reject) => {
            proc.once('error', (err) => {
                if (temporizador) clearTimeout(temporizador);
                reject(err);
            });
            proc.once('close', (code) => {
                if (temporizador) clearTimeout(temporizador);
                try {
                    verificarInode(rutaReal, inode);
                } catch (err) {
                    reject(err);
                    return;
                }
                const stderrTexto = stderrChunks.join('');
                if (vencido) {
                    if (stderrTexto) {
                        reject(new Error(stderrTexto));
                    } else {
                        reject(
                            new Error(
                                `Tiempo de espera agotado al ejecutar '${comando.join(' ')}'`
                            )
                        );
                    }
                    return;
                }
                if (code && code !== 0) {
                    if (stderrTexto) {
                        reject(new Error(stderrTexto));
                    } else {
                        reject(
                            new Error(
                                `Error al ejecutar '${comando.join(' ')}': código ${code}`
                            )
                        );
                    }
                    return;
                }
                resolve();
            });
        });
    } finally {
        if (temporizador) clearTimeout(temporizador);
    }
}

export function obtener_env(nombre) {
    return process.env[nombre];
}

export function listar_dir(ruta) {
    return fs.readdirSync(ruta);
}
