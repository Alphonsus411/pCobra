# src/core/parser.py
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.position = 0

    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        return self.current_token

    def parse(self):
        # Recorre los tokens
        while self.position < len(self.tokens):
            token_type, token_value = self.advance()
            if token_type == 'KEYWORD':
                if token_value == 'funcion':
                    self.parse_function()
                elif token_value == 'si':
                    self.parse_conditional()
                elif token_value == 'mientras':
                    self.parse_loop()

    def parse_function(self):
        print("Parsing a function...")
        # Lógica adicional para parsear funciones

    def parse_conditional(self):
        print("Parsing a conditional (si)...")
        # Lógica para parsear condicionales

    def parse_loop(self):
        print("Parsing a loop (mientras)...")
        # Lógica para parsear bucles

