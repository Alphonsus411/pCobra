class PythonTranspiler:
    def __init__(self, tokens):
        self.tokens = tokens

    def transpile(self):
        # Paso 1: Eliminar las llaves y ajustar la indentación
        codigo_sin_llaves = self.manejar_llaves(self.tokens)

        # Paso 2: Traducir palabras clave de español a Python
        tokens_traducidos = self.traducir_palabras_clave(codigo_sin_llaves.split())

        # Paso 3: Unir el código y ajustar espaciado
        codigo_final = ' '.join(tokens_traducidos)
        codigo_final = self.ajustar_espaciado(codigo_final)

        return codigo_final

    def manejar_llaves(self, tokens):
        # Eliminar las llaves y reemplazarlas con indentación
        resultado = []
        indentacion_nivel = 0

        for token in tokens:
            if token == '{':
                indentacion_nivel += 1
                resultado.append('\n' + '    ' * indentacion_nivel)  # Nueva línea e indentación
            elif token == '}':
                indentacion_nivel -= 1
                if indentacion_nivel > 0:
                    resultado.append('\n' + '    ' * indentacion_nivel)  # Retroceder la indentación
            else:
                resultado.append(token)

        return ''.join(resultado)

    def ajustar_espaciado(self, transpiled_code):
        # Ajustar los espacios alrededor de operadores y palabras clave
        operadores = ['=', '<', '>', '+', '-', '*', '/', 'while', 'if', 'else', 'return']

        for op in operadores:
            transpiled_code = transpiled_code.replace(op, f' {op} ')  # Asegura espacios alrededor de los operadores

        # Limpiar espacios múltiples en blanco
        transpiled_code = ' '.join(transpiled_code.split())

        return transpiled_code

    def traducir_palabras_clave(self, tokens):
        # Traducción de las palabras clave de español a Python
        traducciones = {
            'variable': '',  # 'variable' no se usa en Python
            'funcion': 'def',
            'devolver': 'return',
            'si': 'if',
            'mientras': 'while',
            'mas': 'else',
            'menor': '<',
            'mayor': '>',
            # Se pueden agregar más traducciones aquí según sea necesario
        }

        resultado = [traducciones.get(token, token) for token in tokens]  # Traduce según el diccionario

        return resultado
