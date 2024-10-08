# src/core/lexer.py
class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []

    def tokenize(self):
        keywords = ['si', 'mas', 'mientras', 'funcion', 'variable']  # Añadir más palabras clave según sea necesario
        lines = self.source_code.split("\n")

        for line in lines:
            words = line.split(" ")
            for word in words:
                if word in keywords:
                    self.tokens.append(('KEYWORD', word))
                elif word.isdigit():
                    self.tokens.append(('NUMBER', word))
                elif word.startswith('"') and word.endswith('"'):
                    self.tokens.append(('STRING', word))
                elif word.endswith('()'):  # Si encontramos un identificador de función, eliminamos los paréntesis
                    self.tokens.append(('IDENTIFIER', word[:-2]))
                else:
                    self.tokens.append(('IDENTIFIER', word))

        return self.tokens

