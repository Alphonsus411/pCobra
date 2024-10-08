# src/core/transpiler/js_transpiler.py
class JSTranspiler:
    def __init__(self, tokens):
        self.tokens = tokens
        self.transpiled_code = []

    def transpile(self):
        for token_type, token_value in self.tokens:
            if token_type == 'KEYWORD':
                if token_value == 'si':
                    self.transpiled_code.append('if')
                elif token_value == 'mas':
                    self.transpiled_code.append('else')
                elif token_value == 'mientras':
                    self.transpiled_code.append('while')
            elif token_type == 'NUMBER' or token_type == 'STRING':
                self.transpiled_code.append(token_value)
            else:
                self.transpiled_code.append(token_value)

        # Cambiar \n por un espacio
        return " ".join(self.transpiled_code)
