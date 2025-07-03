const vscode = require('vscode');
const cp = require('child_process');
const { LanguageClient } = require('vscode-languageclient/node');

// Ruta al módulo del servidor LSP. Modifica aquí si cambia el nombre.
const SERVER_MODULE = 'lsp.server';

let client;

function activate(context) {
    console.log('Extensión Cobra activada');

    const disposable = vscode.commands.registerCommand('cobra.startLSP', () => {
        if (client) {
            vscode.window.showInformationMessage('El servidor ya está en ejecución.');
            return;
        }

        const serverOptions = () => {
            const process = cp.spawn('python', ['-m', SERVER_MODULE]);
            return { process };
        };

        const clientOptions = {
            documentSelector: [{ scheme: 'file', language: 'cobra' }],
        };

        client = new LanguageClient('cobra-lsp', 'Cobra LSP', serverOptions, clientOptions);
        context.subscriptions.push(client.start());
    });

    context.subscriptions.push(disposable);

    const runFileDisposable = vscode.commands.registerCommand('cobra.runFile', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No hay un editor activo.');
            return;
        }

        const filePath = editor.document.fileName;

        const output = vscode.window.createOutputChannel('Cobra');
        output.clear();
        output.show(true);

        const proc = cp.spawn('cobra', ['ejecutar', filePath]);

        proc.stdout.on('data', data => output.append(data.toString()));
        proc.stderr.on('data', data => output.append(data.toString()));
        proc.on('error', err => output.append(`Error: ${err.message}\n`));
    });

    context.subscriptions.push(runFileDisposable);
}

function deactivate() {
    if (client) {
        return client.stop();
    }
}

module.exports = { activate, deactivate };
