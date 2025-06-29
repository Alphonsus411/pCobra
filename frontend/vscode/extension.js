const vscode = require('vscode');
const cp = require('child_process');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

function activate(context) {
    console.log('Extensión Cobra activada');

    const disposable = vscode.commands.registerCommand('cobra.startLSP', () => {
        if (client) {
            vscode.window.showInformationMessage('El servidor ya está en ejecución.');
            return;
        }

        const serverOptions = () => {
            const process = cp.spawn('python', ['-m', 'lsp.server']);
            return { process };
        };

        const clientOptions = {
            documentSelector: [{ scheme: 'file', language: 'cobra' }],
        };

        client = new LanguageClient('cobra-lsp', 'Cobra LSP', serverOptions, clientOptions);
        context.subscriptions.push(client.start());
    });

    context.subscriptions.push(disposable);
}

function deactivate() {
    if (client) {
        return client.stop();
    }
}

module.exports = { activate, deactivate };
