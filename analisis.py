import re
import ply.lex as lex

class AnalizadorC:
    def __init__(self, textEdit):
        self.textEdit = textEdit

    def analize_content(self, file_path):
        """Analiza el contenido de un archivo .c y guarda los resultados en trad.txt usando re."""
        try:
            with open(file_path, "r", encoding="utf-8") as source_file:
                content = source_file.read()
            
            lines = content.splitlines()

            palabras_reservadas_C = [
                "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else",
                "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register",
                "restrict", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
                "union", "unsigned", "void", "volatile", "while", "include"
            ]

            simbolos = ['#', '<', '>', '(', ')', '{', '}', ';', ',', '.', '+', '-', '*', '/', '=', '[', ']']

            token_regex = r'(//.*|/\*.*?\*/|\".*?\"|\'.*?\'|\#include\s*<.*?>|\b[A-Za-z_][A-Za-z0-9_]*\.h\b|\b[A-Za-z_][A-Za-z0-9_]*\b|\b\d+\.\d+|\b\d+\b|[!#\\+<>=\[\]{}();,.-])'

            with open("trad.txt", "w", encoding="utf-8") as file:
                for line in lines:
                    tokens = re.findall(token_regex, line)
                    tokens = [t.strip() for t in tokens if t.strip()]
                    for token in tokens:
                        if token in palabras_reservadas_C:
                            file.write(f"Palabra_Reservada: {token}\n")
                        elif token in simbolos:
                            file.write(f"Simbolo: {token}\n")
                        elif re.match(r'\d+', token):
                            file.write(f"Numero: {token}\n")
                        elif re.match(r'\".*?\"|\'.*?\'', token):
                            file.write(f"Cadena: {token}\n")
                        elif re.match(r'\#include\s*<.*?>', token):
                            file.write(f"Libreria: {token}\n")
                        elif token.startswith('//') or token.startswith('/*'):
                            file.write(f"Comentario: {token}\n")
                        else:
                            file.write(f"Identificador: {token}\n")

            print(f"Análisis completado y guardado en trad.txt desde {file_path}")

        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
        except Exception as e:
            print(f"Error al analizar el archivo: {str(e)}")
    
    def generar_traduccion(self):
        """Lee trad.txt y genera traduccion.txt con palabras reservadas traducidas."""
        dicc_palabras_reservadas = {
            "auto": "automatico", "break": "romper", "case": "caso", "char": "caracter",
            "const": "constante", "continue": "continuar", "default": "defecto", "do": "hacer",
            "double": "doble", "else": "sino", "enum": "enumeracion", "extern": "externo",
            "float": "flotante", "for": "para", "goto": "ir_a", "if": "si", "inline": "en_linea",
            "int": "entero", "long": "largo", "register": "registro", "restrict": "restringido",
            "return": "retornar", "short": "corto", "signed": "con_signo", "sizeof": "tamaño_de",
            "static": "estatico", "struct": "estructura", "switch": "selector", "typedef": "definir_tipo",
            "union": "union", "unsigned": "sin_signo", "void": "vacio", "volatile": "volatil", 
            "while": "mientras", "include": "incluir"
        }

        try:
            with open("trad.txt", "r", encoding="utf-8") as trad_file:
                lineas_trad = trad_file.readlines()

            codigo_traducido = []
            linea_actual = ""

            for linea in lineas_trad:
                if not linea.strip():
                    continue

                tipo, token = linea.strip().split(": ", 1)

                if tipo == "Palabra_Reservada":
                    linea_actual += dicc_palabras_reservadas.get(token, token) + " "
                elif tipo == "Comentario":
                    if linea_actual.strip():
                        codigo_traducido.append(linea_actual.strip())
                        linea_actual = ""
                    codigo_traducido.append(token)  # Agregar comentario tal cual
                elif tipo == "Simbolo" and token in [";", "{", "}", ")", ">", "]"]:
                    linea_actual = linea_actual.rstrip() + " " + token + " "
                elif tipo == "Simbolo":
                    linea_actual += token + " "
                elif tipo == "Libreria":
                    if linea_actual.strip():
                        codigo_traducido.append(linea_actual.strip())
                        linea_actual = ""
                    codigo_traducido.append(token)  # Agregar librería tal cual
                else:
                    linea_actual += token + " "

                if token in [";", "{", "}"]:
                    codigo_traducido.append(linea_actual.strip())
                    linea_actual = ""

            # Agregar última línea si queda algo
            if linea_actual.strip():
                codigo_traducido.append(linea_actual.strip())

            # Escribir en traduccion.txt
            with open("traduccion.txt", "w", encoding="utf-8") as out_file:
                out_file.write("\n".join(codigo_traducido))

            print("Traducción completada y guardada en traduccion.txt")

        except Exception as e:
            print(f"Error al generar la traducción: {str(e)}")


class TraductorC:
    def __init__(self):
        self.tokens = (
            'PALABRA_RESERVADA', 'SIMBOLO', 'NUMERO', 'CADENA', 'LIBRERIA', 'COMENTARIO', 'IDENTIFICADOR', 'IDENTIFICADOR_FUNCION'
        )

        self.dicc_palabras_reservadas = {
            "auto": "automatico", "break": "romper", "case": "caso", "char": "caracter",
            "const": "constante", "continue": "continuar", "default": "defecto", "do": "hacer",
            "double": "doble", "else": "sino", "enum": "enumeracion", "extern": "externo",
            "float": "flotante", "for": "para", "goto": "ir_a", "if": "si", "inline": "en_linea",
            "int": "entero", "long": "largo", "register": "registro", "restrict": "restringido",
            "return": "retornar", "short": "corto", "signed": "con_signo", "sizeof": "tamaño_de",
            "static": "estatico", "struct": "estructura", "switch": "selector", "typedef": "definir_tipo",
            "union": "union", "unsigned": "sin_signo", "void": "vacio", "volatile": "volatil",
            "while": "mientras", "include": "incluir"
        }

        self.lexer = lex.lex(module=self)

    t_ignore = ' \t'

    def t_PALABRA_RESERVADA(self, t):
        r'Palabra_Reservada: .*'
        token = t.value.split(': ')[1]
        t.value = self.dicc_palabras_reservadas.get(token, token)
        return t

    def t_SIMBOLO(self, t):
        r'Simbolo: .*'
        t.value = t.value.split(': ')[1]
        return t

    def t_NUMERO(self, t):
        r'Numero: .*'
        t.value = t.value.split(': ')[1]
        return t

    def t_CADENA(self, t):
        r'Cadena: .*'
        t.value = t.value.split(': ')[1]
        return t

    def t_LIBRERIA(self, t):
        r'Libreria: \#include\s*<.*?>'
        t.value = t.value.split(': ')[1]
        return t

    def t_COMENTARIO(self, t):
        r'Comentario: .*'
        t.value = t.value.split(': ')[1]
        return t

    def t_IDENTIFICADOR(self, t):
        r'Identificador: .*'
        t.value = t.value.split(': ')[1]
        return t

    def t_IDENTIFICADOR_FUNCION(self, t):
        r'Identificador: [A-Za-z_][A-Za-z0-9_]*\('  # Detectar identificador seguido de '('
        t.value = t.value.split(': ')[1].split('(')[0]  # Extraer solo el nombre de la función
        return t

    def t_error(self, t):
        print(f"Caracter ilegal: {t.value[0]}")
        t.lexer.skip(1)

    def traducir(self):
        """Lee trad.txt y genera traduccion.txt usando PLY."""
        with open("trad.txt", "r", encoding="utf-8") as file:
            data = file.read()

        self.lexer.input(data)

        codigo_traducido = []
        linea_actual = ""
        
        while True:
            tok = self.lexer.token()
            if not tok:
                break

            if tok.type == "PALABRA_RESERVADA":
                # Traducir la palabra reservada
                linea_actual += self.dicc_palabras_reservadas.get(tok.value, tok.value) + " "
            elif tok.type == "COMENTARIO":
                # Mantener los comentarios en una nueva línea
                if linea_actual.strip():
                    codigo_traducido.append(linea_actual.strip())
                    linea_actual = ""
                codigo_traducido.append(tok.value)  # Agregar comentario tal cual
            elif tok.type == "IDENTIFICADOR_FUNCION":
                # Añadir identificador de función
                if linea_actual.strip():  # Si ya hay algo en la línea, agregarlo
                    codigo_traducido.append(linea_actual.strip())
                    linea_actual = ""
                linea_actual += f"Identificador_de_funcion: {tok.value} "
            elif tok.type == "SIMBOLO":
                # Mantener los símbolos intactos
                linea_actual += tok.value + " "
            elif tok.type == "LIBRERIA":
                # Mantener la librería completa y agregarla con un salto de línea
                if linea_actual.strip():
                    codigo_traducido.append(linea_actual.strip())
                    linea_actual = ""
                codigo_traducido.append(tok.value)  # Agregar la librería con un salto de línea
            else:
                # Otros tipos (números, cadenas, identificadores)
                linea_actual += tok.value + " "

            if tok.type in ["SIMBOLO"] and tok.value in [";", "{", "}"]:
                # Al encontrar símbolos como ;, {, }, agregar la línea
                codigo_traducido.append(linea_actual.strip())
                linea_actual = ""

        # Si queda algo sin agregar en linea_actual
        if linea_actual.strip():
            codigo_traducido.append(linea_actual.strip())

        # Escribir en traduccion.txt
        with open("traduccion.txt", "w", encoding="utf-8") as out_file:
            for line in codigo_traducido:
                out_file.write(line + "\n")

        print("Traducción completada y guardada en traduccion.txt.")


analizador = AnalizadorC(None)  # No usamos textEdit aquí
ruta_archivo = r"hello.c"
analizador.analize_content(ruta_archivo)

traductor = TraductorC()
traductor.traducir()