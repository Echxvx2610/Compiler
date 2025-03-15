from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtPrintSupport import *
import sys
import re

# modulo propio
from resources.tools import banner

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setStyleSheet("background: rgba(0, 0, 0, 0);")

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Using the global background color (same as QTextEdit)
        painter.fillRect(event.rect(), QColor(84, 87, 134))  # Modify this as needed
        painter.setPen(QColor(255, 255, 255))  # White for line numbers

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        offset = self.editor.contentOffset()
        top = self.editor.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, int(top), self.width() - 2, 
                                self.editor.fontMetrics().height(),
                                Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1



class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.load_stylesheet('resources/style/style.qss')

        self.update_line_number_area_width()
        self.highlight_current_line()

        # Configurar la fuente del editor
        font = QFont()
        font.setFamily('Roboto Mono')
        font.setFixedPitch(True)
        font.setPointSize(13)
        self.setFont(font)

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                              self.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(Qt.darkGray).darker(140)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def load_stylesheet(self, file_path):
        """Carga y aplica un archivo QSS."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                stylesheet = file.read()
                # Customizing the QPlainTextEdit widget
                editor_stylesheet = """
                QPlainTextEdit {
                    background-color: rgb(84, 87, 134);
                    color: ghostwhite;
                    border: 1px solid rgb(209, 202, 191);
                    padding: 5px;
                    font-family: 'Roboto Mono';
                    font-size: 13px;
                }
                """
                stylesheet += editor_stylesheet
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error cargando stylesheet: {e}")

class NoteEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        # Establecer icono de la ventana
        self.setWindowIcon(QIcon("resources/img/compilador.png"))

        # Definir variables
        self.title = "Note Editor"
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()

        # Alfabeto
        letra = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

        # Digitos 
        digitos = "0123456789"
        
        # Palabras reservadas
        palabras_reservadas_C = [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", 
            "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", 
            "restrict", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", 
            "union", "unsigned", "void", "volatile", "while", "_Alignas", "_Alignof", "_Atomic", 
            "_Bool", "_Complex", "_Generic", "_Imaginary", "_Noreturn", "_Static_assert", "_Thread_local"
        ]

        # Simbolos
        simbolos = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

        # Operadores aritméticos
        operadores = "+-*/%"

        # Operadores relacionales
        operadores_relacionales = ">=<"

        # Operadores de asignación
        operadores_asignacion = "="

        # Operadores de incremento y decremento
        operadores_incremento_decremento = "++--"

    def initUI(self):
        # Establecer título y geometría de la ventana
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Crear barra de menú
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu("File")
        self.proyectMenu = self.menuBar.addMenu("Proyect")
        self.terminalMenu = self.menuBar.addMenu("Terminal")

        # Crear barra de herramientas
        self.toolBar = self.addToolBar("Main Toolbar")
        self.toolBar.setIconSize(QSize(32, 32))  # Aumentar el tamaño de los iconos

        # Agregar acciones usando la función create_action
        self.newAction = self.create_action("New File", "resources/img/inverted/agregar-archivo.png", self.new_content)
        self.openAction = self.create_action("Open File", "resources/img/inverted/abrir-documento.png", self.load_content)
        self.saveAction = self.create_action("Save File", "resources/img/inverted/disquete.png", self.save_content)
        self.saveAsAction = self.create_action("Save As File", "resources/img/inverted/guardar-el-archivo.png", self.save_content_as)
        self.exitAction = self.create_action("Exit Application", "resources/img/inverted/cerrar-sesion.png", self.close)
        self.analizerAction = self.create_action("Translate", "resources/img/inverted/triangulo.png", self.analize_content)
        self.newTerminal = self.create_action("New Terminal", "resources/img/inverted/comando.png", self.new_terminal)

        # Agregar acciones al menú
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.exitAction)

        self.proyectMenu.addAction(self.analizerAction)
        self.terminalMenu.addAction(self.newTerminal)

        # Agregar acciones a la barra de herramientas
        self.toolBar.addAction(self.newAction)
        self.toolBar.addAction(self.openAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.analizerAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.newTerminal)

        # Orientar la barra de herramientas a la izquierda
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)

        # Crear el editor de código
        self.textEdit = CodeEditor()
        self.setCentralWidget(self.textEdit)

        # Crear la terminal (QTextEdit) en la parte inferior
        self.terminal = QTextEdit(self)
        self.terminal.setReadOnly(True)
        
        # Configurar la fuente monoespaciada
        font = QFont("Roboto Mono", 10)
        font.setStyleHint(QFont.Monospace)
        self.terminal.setFont(font)
        
        # Establecer un ancho de carácter fijo - usando el método correcto para PySide6
        metrics = QFontMetrics(font)
        self.terminal.setTabStopDistance(4 * metrics.horizontalAdvance(' '))
        
        banner_text = banner.get_banner_with_info("Viper Dev")
        self.terminal.setHtml(banner_text)
        # Crear un layout para contener el editor de código y la terminal
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.textEdit)
        self.splitter.addWidget(self.terminal)
        self.setCentralWidget(self.splitter)

        # Aplicar el efecto Frosted Glass/Aero (transparencia y desenfoque)
        self.apply_frosted_glass_effect()

        # Cargar el tema desde style.qss
        self.load_stylesheet("resources/style/style.qss")

        # Mostrar la ventana
        self.show()

    def create_action(self, name, icon_path, function):
        """Crea una acción con un nombre, icono y función de conexión."""
        action = QAction(QIcon(icon_path), name, self)
        action.triggered.connect(function)
        return action

    def load_stylesheet(self, file_path):
        """Carga y aplica un archivo QSS."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                stylesheet = file.read()
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error cargando stylesheet: {e}")

    def apply_frosted_glass_effect(self):
        """Aplica un efecto de vidrio esmerilado (Frosted Glass)."""
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)  # Reduce la opacidad para simular el efecto de "vidrio"

    # Modificar la función `new_terminal` para solo abrir la terminal vacía
    def new_terminal(self):
        """Abre una nueva terminal vacía."""
        self.terminal.clear()  # Limpiar cualquier texto previo
        banner_text = banner.get_banner_with_info("Viper Dev")
        self.terminal.setHtml(banner_text)

    def analize_content(self):
        """
        Analiza el contenido del editor línea por línea y genera tres archivos:
        - trad.txt: Solo tokens, sin sus tipos
        - traduccion.txt: Código C traducido al español
        - errores.txt: Errores sintácticos y léxicos detectados
        """
        
        # Definición de palabras clave y símbolos
        PALABRAS_RESERVADAS = {
            "auto": "automatico", "break": "romper", "case": "caso",
            "char": "caracter", "const": "constante", "continue": "continuar",
            "default": "defecto", "do": "hacer", "double": "doble",
            "else": "sino", "enum": "enumeracion", "extern": "externo",
            "float": "flotante", "for": "para", "goto": "ir_a",
            "if": "si", "inline": "en_linea", "int": "entero",
            "long": "largo", "register": "registro", "restrict": "restringido",
            "return": "retornar", "short": "corto", "signed": "con_signo",
            "sizeof": "tamaño_de", "static": "estatico", "struct": "estructura",
            "switch": "selector", "typedef": "definir_tipo", "union": "union",
            "unsigned": "sin_signo", "void": "vacio", "volatile": "volatil",
            "while": "mientras", "include": "incluir"
        }
        
        SIMBOLOS = ['#', '<', '>', '(', ')', '{', '}', ';', ',', '.', '+', '-', '*', '/', '=', '[', ']']
        
        # Lista de tipos de datos en C
        TIPOS_DATOS = ["int", "float", "char", "double", "void", "long", "short", "unsigned", "signed"]
        
        # Lista de funciones de biblioteca estándar conocidas
        FUNCIONES_BIBLIOTECA = ["printf", "scanf", "fprintf", "fscanf", "sprintf", "sscanf", 
                               "malloc", "calloc", "realloc", "free", "fopen", "fclose", 
                               "fread", "fwrite", "fseek", "ftell", "fgetc", "fputc", 
                               "fgets", "fputs", "strlen", "strcpy", "strncpy", "strcmp", 
                               "strncmp", "strcat", "strncat", "memcpy", "memmove", "memset"]

        def procesar_linea(linea, en_comentario_bloque, comentario_acumulado, num_linea):
            """
            Procesa una línea de código y retorna sus tokens clasificados.
            También maneja el estado de los comentarios de bloque.
            """
            # Detectamos comentarios de línea y bloque primero
            if en_comentario_bloque:
                if '*/' in linea:
                    parte_final = linea[:linea.index('*/') + 2]
                    comentario_acumulado += '\n' + parte_final
                    resto_linea = linea[linea.index('*/') + 2:]
                    tokens_resto, _, _, errores_resto = procesar_linea(resto_linea, False, "", num_linea)
                    return [("Comentario", comentario_acumulado, num_linea)] + tokens_resto, False, "", errores_resto
                else:
                    comentario_acumulado += '\n' + linea
                    return [], True, comentario_acumulado, []

            # Manejar inicio de comentario de bloque
            if '/*' in linea:
                inicio = linea.index('/*')
                # Verificar si el comentario termina en la misma línea
                if '*/' in linea[inicio:]:
                    fin = linea.index('*/', inicio) + 2
                    parte_antes = linea[:inicio]
                    comentario = linea[inicio:fin]
                    parte_despues = linea[fin:]
                    
                    tokens_antes, _, _, errores_antes = procesar_linea(parte_antes, False, "", num_linea) if parte_antes.strip() else ([], False, "", [])
                    tokens_despues, _, _, errores_despues = procesar_linea(parte_despues, False, "", num_linea) if parte_despues.strip() else ([], False, "", [])
                    
                    return tokens_antes + [("Comentario", comentario, num_linea)] + tokens_despues, False, "", errores_antes + errores_despues
                else:
                    parte_antes = linea[:inicio]
                    comentario_acumulado = linea[inicio:]
                    
                    tokens_antes, _, _, errores_antes = procesar_linea(parte_antes, False, "", num_linea) if parte_antes.strip() else ([], False, "", [])
                    
                    return tokens_antes, True, comentario_acumulado, errores_antes

            # Manejar comentarios de línea
            if '//' in linea:
                inicio = linea.index('//')
                parte_antes = linea[:inicio]
                comentario = linea[inicio:]
                
                tokens_antes, _, _, errores_antes = procesar_linea(parte_antes, False, "", num_linea) if parte_antes.strip() else ([], False, "", [])
                
                return tokens_antes + [("Comentario", comentario, num_linea)], False, "", errores_antes

            # Definir patrones regex para cada tipo de token
            patrones = [
                # Cadenas - debe ir primero para evitar conflictos con otros patrones
                (r'"[^"]*"', "Cadena"),
                # Cadenas mal formadas (sin cerrar)
                (r'"[^"]*$', "Cadena_Incompleta"),
                # Carácter
                (r"'.'|'\\.'", "Caracter"),
                # Carácter mal formado
                (r"'[^']*'|'[^']*$", "Caracter_Incompleto"),
                # Librería personalizada
                (r'"[^"]*\.h"', "Libreria_Personalizada"),
                # Librería estándar
                (r'<[^>]*\.h>', "Libreria"),
                # Palabras reservadas y identificadores
                (r'\b[A-Za-z_][A-Za-z0-9_]*\b', "Identificador_O_Reservada"),
                # Números decimales (antes que enteros)
                (r'\b\d+\.\d+\b', "Decimal"),
                # Números enteros
                (r'\b\d+\b', "Entero"),
                # Símbolos
                (r'[#<>()\{\};,.+\-*/=\[\]]', "Simbolo")
            ]
            
            tokens = []
            errores_linea = []
            pos = 0
            linea_restante = linea.strip()
            
            while linea_restante:
                encontrado = False
                for patron, tipo_inicial in patrones:
                    match = re.match(r'^\s*(' + patron + r')', linea_restante)
                    if match:
                        token = match.group(1).strip()
                        # Clasificar el token más específicamente
                        tipo_final = clasificar_token_especifico(tipo_inicial, token, PALABRAS_RESERVADAS, SIMBOLOS, TIPOS_DATOS)
                        tokens.append((tipo_final, token, num_linea))
                        pos += match.end()
                        linea_restante = linea_restante[match.end():].strip()
                        encontrado = True
                        break
                
                if not encontrado:
                    # Si no se encontró un patrón, avanzar un carácter y reportar error
                    caracter_desconocido = linea_restante[0]
                    errores_linea.append(f"Error en Linea {num_linea}: Carácter desconocido: '{caracter_desconocido}'")
                    linea_restante = linea_restante[1:].strip()
            
            # Verificar las relaciones contextuales (por ejemplo, identificadores de función)
            tokens_finales = []
            i = 0
            while i < len(tokens):
                tipo, token, linea_num = tokens[i]
                
                # Detectar identificadores de función
                if tipo == "Identificador" and i < len(tokens) - 1 and tokens[i+1][1] == '(':
                    # Verificar si hay un tipo de dato antes
                    if i > 0 and (tokens[i-1][0] in ["Tipo_Dato"] or tokens[i-1][1] in TIPOS_DATOS):
                        tokens_finales.append(("Identificador_Funcion", token, linea_num))
                    else:
                        tokens_finales.append(("Llamada_Funcion", token, linea_num))
                else:
                    tokens_finales.append((tipo, token, linea_num))
                
                i += 1
            
            return tokens_finales, False, "", errores_linea

        def clasificar_token_especifico(tipo_inicial, token, PALABRAS_RESERVADAS, SIMBOLOS, TIPOS_DATOS):
            """Clasifica un token más específicamente basado en su tipo inicial y valor."""
            if tipo_inicial == "Identificador_O_Reservada":
                if token in PALABRAS_RESERVADAS:
                    return "Palabra_Reservada"
                elif token in TIPOS_DATOS:
                    return "Tipo_Dato"
                else:
                    return "Identificador"
            elif tipo_inicial == "Simbolo":
                return "Simbolo"
            elif tipo_inicial == "Caracter_Incompleto":
                return "Caracter_Error"
            elif tipo_inicial == "Cadena_Incompleta":
                return "Cadena_Error"
            else:
                return tipo_inicial

        def traducir_codigo(tokens_y_formato):
            """Traduce el código usando los tokens y la información de formato."""
            codigo_traducido = []
            linea_actual = []
            
            for item in tokens_y_formato:
                if isinstance(item, str):  # Es indentación
                    if linea_actual:
                        codigo_traducido.append(item + " ".join(linea_actual))
                        linea_actual = []
                    elif item:  # Línea vacía con indentación
                        codigo_traducido.append("")
                else:  # Es un token
                    tipo, token, _ = item
                    if tipo == "Palabra Reservada":
                        token = PALABRAS_RESERVADAS.get(token, token)
                    linea_actual.append(token)
            
            if linea_actual:  # Procesar última línea si existe
                codigo_traducido.append(" ".join(linea_actual))
            
            return "\n".join(codigo_traducido)

        def verificar_errores_tokens(tokens):
            """
            Verifica errores específicos para cada tipo de token.
            Retorna una lista de errores encontrados.
            """
            errores = []
            variables_declaradas = set()
            funciones_declaradas = set()
            
            # Rastrear el ámbito actual usando una pila
            ambitos = [set()]  # Lista de conjuntos de variables
            
            # Rastrear bloques de código
            nivel_bloque = 0
            bloques_anidados = []  # Para rastrear if, for, while, etc.
            
            # Verificar si hay bloques abiertos correctamente
            bloques_abiertos = 0
            parentesis_abiertos = 0
            corchetes_abiertos = 0
            
            # Verificar si estamos dentro de una declaración
            en_declaracion = False
            tipo_actual = None
            
            i = 0
            while i < len(tokens):
                tipo, token, num_linea = tokens[i]
                
                # Verificar apertura y cierre de bloques
                if token == '{':
                    bloques_abiertos += 1
                    # Crear un nuevo ámbito
                    ambitos.append(set())
                elif token == '}':
                    bloques_abiertos -= 1
                    if bloques_abiertos < 0:
                        errores.append(f"Error en Linea {num_linea}: Llave de cierre '}}' sin llave de apertura correspondiente")
                    elif ambitos:
                        # Eliminar el ámbito actual
                        ambitos.pop()
                
                # Verificar paréntesis
                elif token == '(':
                    parentesis_abiertos += 1
                elif token == ')':
                    parentesis_abiertos -= 1
                    if parentesis_abiertos < 0:
                        errores.append(f"Error en Linea {num_linea}: Paréntesis de cierre ')' sin paréntesis de apertura correspondiente")
                
                # Verificar corchetes
                elif token == '[':
                    corchetes_abiertos += 1
                elif token == ']':
                    corchetes_abiertos -= 1
                    if corchetes_abiertos < 0:
                        errores.append(f"Error en Linea {num_linea}: Corchete de cierre ']' sin corchete de apertura correspondiente")
                        
                # Verificar directivas de preprocesador (#include)
                elif token == '#':
                    if i + 1 < len(tokens):
                        siguiente_tipo, siguiente_token, _ = tokens[i + 1]
                        if siguiente_token != "include":
                            errores.append(f"Error en Linea {num_linea}: Se espera 'include' después de '#'")
                        else:
                            # Verificar formato correcto del include
                            if i + 2 < len(tokens):
                                if tokens[i+2][0] not in ["Libreria", "Libreria_Personalizada"] and tokens[i+2][1] not in ['<', '"']:
                                    errores.append(f"Error en Linea {num_linea}: Formato incorrecto después de '#include'")
                    else:
                        errores.append(f"Error en Linea {num_linea}: Directiva de preprocesador incompleta")
                
                # Verificar palabras reservadas
                elif tipo == "Palabra_Reservada":
                    # Estructura de control
                    if token in ["if", "for", "while", "switch"]:
                        # Verificar que haya un paréntesis después
                        if i + 1 >= len(tokens) or tokens[i+1][1] != '(':
                            errores.append(f"Error en Linea {num_linea}: Falta paréntesis después de '{token}'")
                        bloques_anidados.append(token)
                    
                    # Verificar else
                    elif token == "else":
                        # Debe estar precedido por un bloque if
                        if not bloques_anidados or bloques_anidados[-1] != "if":
                            errores.append(f"Error en Linea {num_linea}: 'else' sin 'if' correspondiente")
                        
                        # Verificar si hay un 'if' después (else if)
                        if i + 1 < len(tokens) and tokens[i+1][1] == "if":
                            pass  # Esto es correcto (else if)
                        elif i + 1 < len(tokens) and tokens[i+1][1] != "{":
                            # Debería haber una llave o un 'if' después de else
                            errores.append(f"Error en Linea {num_linea}: Se espera '{{' o 'if' después de 'else'")
                    
                    # Verificar return
                    elif token == "return":
                        # Verificar que haya un punto y coma después
                        j = i + 1
                        while j < len(tokens) and tokens[j][1] != ';':
                            j += 1
                        if j >= len(tokens):
                            errores.append(f"Error en Linea {num_linea}: Falta punto y coma después de 'return'")
                
                # Verificar tipos de datos (para declaraciones)
                elif tipo == "Tipo_Dato" or token in TIPOS_DATOS:
                    en_declaracion = True
                    tipo_actual = token
                
                # Verificar identificadores (variables)
                elif tipo == "Identificador":
                    # Variables en declaración
                    if en_declaracion:
                        if token in [t for ambito in ambitos for t in ambito]:
                            errores.append(f"Error en Linea {num_linea}: Variable '{token}' ya ha sido declarada en este ámbito")
                        else:
                            # Añadir al ámbito actual
                            if ambitos:
                                ambitos[-1].add(token)
                            variables_declaradas.add(token)
                        
                        # Verificar inicialización
                        if i + 1 < len(tokens) and tokens[i+1][1] == '=':
                            # Verificar el valor después del signo igual
                            if i + 2 < len(tokens):
                                valor_tipo, valor, _ = tokens[i+2]
                                if valor_tipo not in ["Entero", "Decimal", "Cadena", "Caracter", "Identificador"]:
                                    errores.append(f"Error en Linea {num_linea}: Valor inválido para inicialización de variable '{token}'")
                        
                        # Verificar punto y coma al final de la declaración
                        j = i + 1
                        while j < len(tokens) and tokens[j][1] not in [';', ',']:
                            j += 1
                        if j >= len(tokens) or tokens[j][1] not in [';', ',']:
                            errores.append(f"Error en Linea {num_linea}: Falta punto y coma o coma en la declaración de '{token}'")
                    
                    # Variables en uso
                    else:
                        # Verificar si la variable ha sido declarada
                        if token not in variables_declaradas and token not in [t for ambito in ambitos for t in ambito]:
                            errores.append(f"Error en Linea {num_linea}: Variable '{token}' usada sin declarar previamente")
                
                # Verificar identificadores de función
                elif tipo == "Identificador_Funcion":
                    funciones_declaradas.add(token)
                    
                    # Verificar parámetros dentro de los paréntesis
                    if i + 1 < len(tokens) and tokens[i+1][1] == '(':
                        # Recorrer hasta el paréntesis de cierre
                        nivel = 1
                        j = i + 2
                        
                        # Lista para almacenar parámetros
                        parametros = []
                        param_actual = []
                        
                        while j < len(tokens) and nivel > 0:
                            if tokens[j][1] == '(':
                                nivel += 1
                            elif tokens[j][1] == ')':
                                nivel -= 1
                                if nivel == 0:
                                    # Añadir el último parámetro si hay algo
                                    if param_actual:
                                        parametros.append(param_actual)
                            elif tokens[j][1] == ',' and nivel == 1:
                                # Fin del parámetro actual
                                parametros.append(param_actual)
                                param_actual = []
                            else:
                                # Añadir a parámetro actual
                                param_actual.append(tokens[j])
                            
                            j += 1
                        
                        # Verificar cada parámetro
                        for param in parametros:
                            # Debe tener un tipo y un nombre
                            if len(param) < 2:
                                errores.append(f"Error en Linea {num_linea}: Parámetro incompleto en función '{token}'")
                            elif param[0][0] != "Tipo_Dato" and param[0][1] not in TIPOS_DATOS:
                                errores.append(f"Error en Linea {num_linea}: Parámetro sin tipo en función '{token}'")
                
                # Verificar llamadas a funciones
                elif tipo == "Llamada_Funcion":
                    if token not in funciones_declaradas and token not in FUNCIONES_BIBLIOTECA:
                        errores.append(f"Error en Linea {num_linea}: Función '{token}' llamada sin declarar")
                    
                    # Verificar punto y coma después de la llamada
                    # Encontrar el paréntesis de cierre
                    nivel = 0
                    j = i
                    while j < len(tokens):
                        if tokens[j][1] == '(':
                            nivel += 1
                        elif tokens[j][1] == ')':
                            nivel -= 1
                            if nivel == 0:
                                break
                        j += 1
                    
                    # Después del paréntesis de cierre debe haber punto y coma
                    if j < len(tokens) - 1 and tokens[j+1][1] != ';':
                        errores.append(f"Error en Linea {tokens[j][2]}: Falta punto y coma ';' después de la llamada a función '{token}'")
                
                # Verificar expresiones con operadores
                elif token in ['+', '-', '*', '/', '=']:
                    # Verificar que haya operandos a ambos lados
                    if i == 0 or i == len(tokens) - 1:
                        errores.append(f"Error en Linea {num_linea}: Operador '{token}' sin operandos suficientes")
                    else:
                        izq_tipo, izq_token, _ = tokens[i-1]
                        
                        # El lado izquierdo debe ser un identificador, número o resultado de expresión
                        if izq_tipo not in ["Identificador", "Entero", "Decimal", "Caracter"] and izq_token != ')':
                            errores.append(f"Error en Linea {num_linea}: Expresión inválida: operando izquierdo de '{token}' no es válido")
                        
                        # Verificar el lado derecho si no estamos al final
                        if i < len(tokens) - 1:
                            der_tipo, der_token, _ = tokens[i+1]
                            if der_tipo not in ["Identificador", "Entero", "Decimal", "Caracter", "Cadena"] and der_token not in ['(', '+', '-']:
                                errores.append(f"Error en Linea {num_linea}: Expresión inválida: operando derecho de '{token}' no es válido")
                
                # Verificar errores de sintaxis de cadenas
                elif tipo == "Cadena_Error":
                    errores.append(f"Error en Linea {num_linea}: Cadena sin cerrar: {token}")
                
                # Verificar errores de sintaxis de caracteres
                elif tipo == "Caracter_Error":
                    errores.append(f"Error en Linea {num_linea}: Caracter mal formado: {token}")
                
                # Verificar punto y coma al final de sentencias
                if token == ';':
                    en_declaracion = False
                    tipo_actual = None
                
                i += 1
            
            # Verificar estructuras no cerradas al final
            if bloques_abiertos > 0:
                errores.append(f"Error: Hay {bloques_abiertos} llaves '{{' sin cerrar")
            if parentesis_abiertos > 0:
                errores.append(f"Error: Hay {parentesis_abiertos} paréntesis '(' sin cerrar")
            if corchetes_abiertos > 0:
                errores.append(f"Error: Hay {corchetes_abiertos} corchetes '[' sin cerrar")
            
            return errores

        def verificar_estructura_sintactica(tokens):
            """
            Verifica la estructura sintáctica del código (llaves, paréntesis, punto y coma).
            Retorna una lista de errores encontrados.
            """
            errores = []
            balance_llaves = 0
            balance_parentesis = 0
            espera_punto_y_coma = False
            
            i = 0
            while i < len(tokens):
                tipo, token, num_linea = tokens[i]
                
                # Ignorar comentarios
                if tipo == "Comentario":
                    i += 1
                    continue
                    
                # Verificar balance de llaves
                if token == '{':
                    balance_llaves += 1
                    espera_punto_y_coma = False  # Resetear después de una llave
                elif token == '}':
                    balance_llaves -= 1
                    espera_punto_y_coma = False  # Resetear después de una llave
                    if balance_llaves < 0:
                        errores.append(f"Error en Linea {num_linea}: Llave de cierre '}}' sin llave de apertura correspondiente")
                        balance_llaves = 0  # Restablecer para evitar errores en cascada
                
                # Verificar balance de paréntesis
                if token == '(':
                    balance_parentesis += 1
                elif token == ')':
                    balance_parentesis -= 1
                    if balance_parentesis < 0:
                        errores.append(f"Error en Linea {num_linea}: Paréntesis de cierre ')' sin paréntesis de apertura correspondiente")
                        balance_parentesis = 0  # Restablecer para evitar errores en cascada
                
                # Mejorar detección de punto y coma faltante
                # Verificación especial para return
                if token == "return":
                    # Buscar si hay punto y coma después de la expresión de return
                    encontrado_punto_y_coma = False
                    j = i + 1
                    while j < len(tokens) and tokens[j][1] not in [';', '{', '}']:
                        j += 1
                    
                    if j < len(tokens) and tokens[j][1] == ';':
                        encontrado_punto_y_coma = True
                    
                    if not encontrado_punto_y_coma:
                        errores.append(f"Error en Linea {num_linea}: Falta punto y coma ';' después de la expresión 'return'")
                
                # Verificar si necesita punto y coma
                if espera_punto_y_coma:
                    if token != ';' and token != '{' and token != '}':
                        # Solo verificar al final de una instrucción
                        if i + 1 < len(tokens):
                            siguiente_token = tokens[i+1][1]
                            if siguiente_token in ['{', '}']:
                                # Estamos al final de una instrucción
                                errores.append(f"Error en Linea {num_linea}: Falta punto y coma ';' después de '{token}'")
                    espera_punto_y_coma = False
                
                # Después de declaraciones de variables o expresiones
                if tipo in ["Identificador", "Entero", "Decimal", "Cadena", "Caracter","Identificador de Funcion"]:
                    if i + 1 < len(tokens):
                        siguiente_token = tokens[i+1][1]
                        if siguiente_token not in [';', ',', ')', ']', '+', '-', '*', '/', '=']:
                            espera_punto_y_coma = True
                
                # Verificar estructuras de control
                if tipo == "Palabra Reservada":
                    if token in ["if", "while", "for", "switch"]:
                        # Verificar que después venga un paréntesis
                        if i + 1 >= len(tokens) or tokens[i+1][1] != '(':
                            errores.append(f"Error en Linea {num_linea}: Falta paréntesis '(' después de '{token}'")
                    
                    elif token in ["else"]:
                        # Verificar que después venga un if o una llave
                        if i + 1 < len(tokens) and tokens[i+1][1] != 'if' and tokens[i+1][1] != '{':
                            errores.append(f"Error en Linea {num_linea}: Se espera 'if' o '{{' después de 'else'")
                
                i += 1
            
            # Verificar balance final de llaves y paréntesis
            if balance_llaves > 0:
                errores.append(f"Error: Faltan {balance_llaves} llaves de cierre '}}'")
            if balance_parentesis > 0:
                errores.append(f"Error: Faltan {balance_parentesis} paréntesis de cierre ')'")
            
            return errores

        # Obtener el contenido del editor
        contenido = self.textEdit.toPlainText()
        lineas = contenido.splitlines()
        
        # Para almacenar tokens y formato para la traducción
        tokens_y_formato = []
        # Para almacenar solo los tokens para trad.txt
        tokens_para_archivo = []
        # Para almacenar todos los tokens con su información
        todos_los_tokens = []
        # Para almacenar errores
        todos_los_errores = []
        
        # Variables para manejar comentarios de bloque
        en_comentario_bloque = False
        comentario_acumulado = ""
        
        # Procesar cada línea
        for num_linea, linea in enumerate(lineas, 1):
            indentacion = " " * (len(linea) - len(linea.lstrip()))
            tokens_y_formato.append(indentacion)
            
            if not linea.strip():
                continue
            
            tokens, en_comentario_bloque, comentario_acumulado, errores_linea = procesar_linea(
                linea, en_comentario_bloque, comentario_acumulado, num_linea
            )
            
            # Agregar errores detectados durante el procesamiento de la línea
            todos_los_errores.extend(errores_linea)
            
            if tokens:  # Si hay tokens en la línea
                tokens_y_formato.extend(tokens)
                todos_los_tokens.extend(tokens)
                
                # Agregar SOLO los tokens al archivo trad.txt (sin sus tipos)
                for _, valor, _ in tokens:
                    tokens_para_archivo.append(valor)
                tokens_para_archivo.append("")  # Línea vacía entre líneas de código
        
        # Si terminamos con un comentario de bloque sin cerrar
        if en_comentario_bloque:
            todos_los_errores.append(f"Error: Comentario de bloque sin cerrar, comenzado en línea {todos_los_tokens[-1][2] if todos_los_tokens else 'desconocida'}")
        
        # Guardar solo los tokens en trad.txt (sin sus tipos)
        with open("trad.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(tokens_para_archivo).rstrip())
        
        # Generar y guardar código traducido
        codigo_traducido = traducir_codigo(tokens_y_formato)
        with open("traduccion.txt", "w", encoding="utf-8") as f:
            f.write(codigo_traducido)
        
        # Realizar análisis de errores específicos por tipo de token
        errores_tokens = verificar_errores_tokens(todos_los_tokens)
        todos_los_errores.extend(errores_tokens)
        
        # Realizar análisis de estructura sintáctica
        errores_estructura = verificar_estructura_sintactica(todos_los_tokens)
        todos_los_errores.extend(errores_estructura)
        
        # Guardar errores
        with open("errores.txt", "w", encoding="utf-8") as f:
            if todos_los_errores:
                f.write("\n".join(todos_los_errores))
            else:
                f.write("No se encontraron errores léxicos ni sintácticos.")
        
        print("Análisis léxico, sintáctico y traducción completados correctamente.")

    def new_content(self):
        """Limpia el área de texto del editor de código y resetea la referencia al archivo actual."""
        self.textEdit.clear()
        self.current_file = None  # Restablecer la referencia al archivo actual
        print("Nuevo documento creado.")


    def save_content(self):
        """Guarda el contenido del área de texto en un archivo (sobreescribe si ya existe)."""
        if hasattr(self, 'current_file') and self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.textEdit.toPlainText())
                print(f"Contenido guardado en {self.current_file}")
            except Exception as e:
                print(f"Error al guardar el archivo: {e}")
        else:
            self.save_content_as()


    def save_content_as(self):
        """Permite guardar el contenido en una ubicación y formato deseados."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar archivo como", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=options)
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(self.textEdit.toPlainText())
                self.current_file = file_name  # Actualiza la ruta del archivo actual
                print(f"Contenido guardado en {file_name}")
            except Exception as e:
                print(f"Error al guardar el archivo: {e}")


    def load_content(self):
        """Carga un archivo de texto en el área de edición."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos C (*.c);;Todos los archivos (*)", options=options)
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.textEdit.setPlainText(file.read())
                self.current_file = file_name  # Guarda la ruta del archivo cargado
                print(f"Archivo cargado desde {file_name}")
            except Exception as e:
                print(f"Error al cargar el archivo: {e}")


if __name__ == '__main__':
    application = QApplication(sys.argv)
    editor = NoteEditor()
    sys.exit(application.exec())
