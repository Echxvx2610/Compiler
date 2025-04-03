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
        
        Utiliza PLY (Python Lex-Yacc) para el análisis léxico y sintáctico.
        """
        import ply.lex as lex
        import re
        
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
        
        # Lista de tipos de datos en C
        TIPOS_DATOS = ["int", "float", "char", "double", "void", "long", "short", "unsigned", "signed"]
        
        # Lista de funciones de biblioteca estándar conocidas
        FUNCIONES_BIBLIOTECA = ["printf", "scanf", "fprintf", "fscanf", "sprintf", "sscanf", 
                            "malloc", "calloc", "realloc", "free", "fopen", "fclose", 
                            "fread", "fwrite", "fseek", "ftell", "fgetc", "fputc", 
                            "fgets", "fputs", "strlen", "strcpy", "strncpy", "strcmp", 
                            "strncmp", "strcat", "strncat", "memcpy", "memmove", "memset"]
        
        # Error de seguimiento y tracking
        errores_lexicos = []
        todos_los_tokens = []
        tokens_y_formato = []
        
        # Crear una clase Lexer para mejor organización
        class CLexer:
            # Lista de tokens a reconocer
            tokens = [
                'PALABRA_RESERVADA',
                'TIPO_DATO',
                'IDENTIFICADOR',
                'IDENTIFICADOR_FUNCION',
                'LLAMADA_FUNCION',
                'MAIN_FUNCTION',
                'ENTERO',
                'DECIMAL',
                'CADENA',
                'CADENA_ERROR',
                'CARACTER',
                'CARACTER_ERROR',
                'SIMBOLO',
                'LIBRERIA',
                'LIBRERIA_PERSONALIZADA',
                'COMENTARIO',
                'ERROR'
            ]
            
            # Estados del analizador léxico
            states = (
                ('comentario', 'exclusive'),
            )
            
            # Tokens para el estado INITIAL
            
            # Iniciar comentario de bloque
            def t_COMENTARIO_INICIO(self, t):
                r'/\*'
                t.lexer.begin('comentario')
                t.lexer.comentario_texto = t.value
                return None
            
            # Comentario de línea
            def t_COMENTARIO_LINEA(self, t):
                r'//.*'
                t.type = 'COMENTARIO'
                todos_los_tokens.append(('Comentario', t.value, t.lineno))
                tokens_y_formato.append(('Comentario', t.value, t.lineno))
                return t
            
            # Bibliotecas
            def t_LIBRERIA(self, t):
                r'<[^>]*\.h>'
                todos_los_tokens.append(('Libreria', t.value, t.lineno))
                tokens_y_formato.append(('Libreria', t.value, t.lineno))
                return t
            
            def t_LIBRERIA_PERSONALIZADA(self, t):
                r'"[^"]*\.h"'
                todos_los_tokens.append(('Libreria_Personalizada', t.value, t.lineno))
                tokens_y_formato.append(('Libreria_Personalizada', t.value, t.lineno))
                return t
            
            # Cadenas
            def t_CADENA(self, t):
                r'"[^"]*"'
                todos_los_tokens.append(('Cadena', t.value, t.lineno))
                tokens_y_formato.append(('Cadena', t.value, t.lineno))
                return t
            
            def t_CADENA_ERROR(self, t):
                r'"[^"]*$'
                errores_lexicos.append(f"Error en Linea {t.lineno}: Cadena sin cerrar: {t.value}")
                todos_los_tokens.append(('Cadena_Error', t.value, t.lineno))
                tokens_y_formato.append(('Cadena_Error', t.value, t.lineno))
                return t
            
            # Caracteres
            def t_CARACTER(self, t):
                r"'.'|'\\.'|'\\\\'"
                todos_los_tokens.append(('Caracter', t.value, t.lineno))
                tokens_y_formato.append(('Caracter', t.value, t.lineno))
                return t
            
            def t_CARACTER_ERROR(self, t):
                r"'[^']*'|'[^']*$"
                if len(t.value) > 3 or not t.value.endswith("'"):
                    errores_lexicos.append(f"Error en Linea {t.lineno}: Caracter mal formado: {t.value}")
                    todos_los_tokens.append(('Caracter_Error', t.value, t.lineno))
                    tokens_y_formato.append(('Caracter_Error', t.value, t.lineno))
                return t
            
            # Números
            def t_DECIMAL(self, t):
                r'\b\d+\.\d+\b'
                todos_los_tokens.append(('Decimal', t.value, t.lineno))
                tokens_y_formato.append(('Decimal', t.value, t.lineno))
                return t
            
            def t_ENTERO(self, t):
                r'\b\d+\b'
                todos_los_tokens.append(('Entero', t.value, t.lineno))
                tokens_y_formato.append(('Entero', t.value, t.lineno))
                return t
            
            # Identificadores y palabras clave
            def t_IDENTIFICADOR(self, t):
                r'\b[A-Za-z_][A-Za-z0-9_]*\b'
                # Clasificar según el contenido del token
                if t.value in PALABRAS_RESERVADAS:
                    t.type = 'PALABRA_RESERVADA'
                    todos_los_tokens.append(('Palabra_Reservada', t.value, t.lineno))
                    tokens_y_formato.append(('Palabra_Reservada', t.value, t.lineno))
                elif t.value in TIPOS_DATOS:
                    t.type = 'TIPO_DATO'
                    todos_los_tokens.append(('Tipo_Dato', t.value, t.lineno))
                    tokens_y_formato.append(('Tipo_Dato', t.value, t.lineno))
                else:
                    # Aquí solo hacemos la clasificación básica, las funciones se detectarán en post-procesamiento
                    t.type = 'IDENTIFICADOR'
                    todos_los_tokens.append(('Identificador', t.value, t.lineno))
                    tokens_y_formato.append(('Identificador', t.value, t.lineno))
                return t
            
            # Símbolos
            def t_SIMBOLO(self, t):
                r'[#<>()\{\};,.+\-*/=\[\]]'
                todos_los_tokens.append(('Simbolo', t.value, t.lineno))
                tokens_y_formato.append(('Simbolo', t.value, t.lineno))
                return t
            
            # Espacios y formato
            def t_ESPACIO(self, t):
                r'[ \t]+'
                # Guardamos el espacio para preservar formato
                return None
            
            # Saltos de línea
            def t_newline(self, t):
                r'\n+'
                t.lexer.lineno += len(t.value)
                tokens_y_formato.append('\n' * len(t.value))  # Para mantener el formato
                return None
            
            # Error general
            def t_error(self, t):
                errores_lexicos.append(f"Error en Linea {t.lineno}: Carácter ilegal {t.value[0]}")
                t.lexer.skip(1)
            
            # Reglas para el estado de comentario
            def t_comentario_CONTENIDO(self, t):
                r'[^*]+'
                t.lexer.comentario_texto += t.value
                return None
            
            def t_comentario_ASTERISCO(self, t):
                r'\*(?!\/)' 
                t.lexer.comentario_texto += t.value
                return None
            
            def t_comentario_FIN(self, t):
                r'\*/'
                t.lexer.comentario_texto += t.value
                t.type = 'COMENTARIO'
                t.value = t.lexer.comentario_texto
                t.lexer.begin('INITIAL')
                todos_los_tokens.append(('Comentario', t.value, t.lineno))
                tokens_y_formato.append(('Comentario', t.value, t.lineno))
                return t
            
            # Error en estado de comentario
            def t_comentario_error(self, t):
                errores_lexicos.append(f"Error en el comentario de bloque en Linea {t.lineno}: {t.value[0]}")
                t.lexer.skip(1)
        
        # Instanciamos el lexer
        lexer_instance = CLexer()
        lexer = lex.lex(module=lexer_instance)
        
        # Configuramos el lexer
        lexer.lineno = 1
        lexer.comentario_texto = ''
        
        # Obtener el contenido del editor
        contenido = self.textEdit.toPlainText()
        
        # Analizamos el contenido
        lexer.input(contenido)
        
        # Obtenemos todos los tokens
        token_lista_raw = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            token_lista_raw.append(tok)
        
        # Post-procesamiento para detectar funciones y características más avanzadas
        def post_procesar_tokens():
            """
            Realiza un post-procesamiento de los tokens para detectar funciones y
            otras características contextuales, incluyendo validación de estructuras de control.
            """
            todos_los_tokens_procesados = []
            variables_declaradas = set()
            funciones_declaradas = set()
            ambitos = [set()]  # Lista de conjuntos de variables
            llaves_apertura = []  # [(linea, contexto), ...]
            bloques_esperando_llave = []
            errores_sintacticos = []
            
            # Para rastrear bloques if pendientes de cierre (para validación de else)
            bloques_if_abiertos = []
            
            i = 0
            while i < len(todos_los_tokens):
                tipo, token, num_linea = todos_los_tokens[i]
                
                # Detectar identificadores de función (igual que antes)
                if tipo == "Identificador" and i < len(todos_los_tokens) - 1 and todos_los_tokens[i+1][1] == '(':
                    # Verificar si hay un tipo de dato antes
                    if i > 0 and (todos_los_tokens[i-1][0] == "Tipo_Dato" or todos_los_tokens[i-1][1] in TIPOS_DATOS):
                        nuevo_tipo = "Identificador_Funcion"
                        funciones_declaradas.add(token)
                        if token == "main":
                            nuevo_tipo = "Main_Function"
                    else:
                        nuevo_tipo = "Llamada_Funcion"
                    
                    todos_los_tokens_procesados.append((nuevo_tipo, token, num_linea))
                else:
                    todos_los_tokens_procesados.append((tipo, token, num_linea))
                
                # Detectar errores en identificadores que podrían ser palabras reservadas mal escritas
                # if tipo == "Identificador":
                #     # Cuando detectas un identificador que podría ser una palabra reservada mal escrita
                #     # Añade una condición para excluir cuando es claramente una variable en un bucle for
                #     es_variable_en_for = False
                #     if i > 1 and todos_los_tokens[i-2][1] == 'for' and todos_los_tokens[i-1][1] == '(':
                #         # Estamos dentro de un bucle for después del paréntesis de apertura
                #         es_variable_en_for = True
                #     # O si estamos en una expresión de iteración (i++)
                #     elif i > 0 and i < len(todos_los_tokens) - 1:
                #         if token == 'i' and todos_los_tokens[i+1][1] in ['++', '+=', '--', '-=']:
                #             es_variable_en_for = True
                    
                #     # Sólo verificar errores de escritura si no es una variable legítima
                #     if not es_variable_en_for and token in palabras_similares:
                #         errores_sintacticos.append(f"Error en Linea {num_linea}: Posible error de escritura '{token}', ¿quizás quiso decir '{palabras_similares[token]}'?")
                    
                #     # Diccionario de posibles errores de escritura y sus correcciones
                #     palabras_similares = {
                #         "i": "if", "f": "if", "fi": "if", 
                #         "whil": "while", "whlie": "while", "wile": "while",
                #         "fo": "for", "fr": "for", "fro": "for","ese": "else",
                #         "els": "else", "eles": "else", "lese": "else",
                #         "switc": "switch", "swich": "switch", "swith": "switch",
                #         "casse": "case", "cas": "case", "cse": "case",
                #         "dafault": "default", "defult": "default", "defalt": "default",
                #         "brak": "break", "brk": "break", "brek": "break",
                #         "retur": "return", "retrun": "return", "retrn": "return",
                #         "continu": "continue", "contiue": "continue", "cotinue": "continue",
                #         "flaot": "float", "flot": "float", "flt": "float",
                #         "duble": "double", "doulbe": "double", "doubel": "double",
                #         "vod": "void", "viod": "void", "vid": "void",
                #         "inclde": "include", "includ": "include", "iclude": "include"
                #     }
                    
                #     # Verificar si el identificador podría ser una palabra reservada mal escrita
                #     if token in palabras_similares:
                #         errores_sintacticos.append(f"Error en Linea {num_linea}: Posible error de escritura '{token}', ¿quizás quiso decir '{palabras_similares[token]}'?")
                    
                #     # También podemos usar la distancia de edición para identificar errores más complejos
                #     # (esto sería una mejora adicional si se necesita)
                # Detectar errores en identificadores que podrían ser palabras reservadas mal escritas
                if tipo == "Identificador":
                    # Diccionario de posibles errores de escritura y sus correcciones
                    palabras_similares = {
                        "i": "if", "f": "if", "fi": "if", 
                        "whil": "while", "whlie": "while", "wile": "while",
                        "fo": "for", "fr": "for", "fro": "for","ese": "else",
                        "els": "else", "eles": "else", "lese": "else",
                        "switc": "switch", "swich": "switch", "swith": "switch",
                        "casse": "case", "cas": "case", "cse": "case",
                        "dafault": "default", "defult": "default", "defalt": "default",
                        "brak": "break", "brk": "break", "brek": "break",
                        "retur": "return", "retrun": "return", "retrn": "return",
                        "continu": "continue", "contiue": "continue", "cotinue": "continue",
                        "flaot": "float", "flot": "float", "flt": "float",
                        "duble": "double", "doulbe": "double", "doubel": "double",
                        "vod": "void", "viod": "void", "vid": "void",
                        "inclde": "include", "includ": "include", "iclude": "include"
                    } 
                    # Verificar si el identificador podría ser una palabra reservada mal escrita
                    if token in palabras_similares:
                        # Verificar si estamos en un contexto donde este identificador es válido
                        es_variable_valida = False
                        
                        # Para 'i', comprobar si está en un bucle for
                        if token == "i":
                            # 1. Buscar un 'for' reciente
                            for_encontrado = False
                            for j in range(max(0, i-5), i):
                                if j < len(todos_los_tokens) and todos_los_tokens[j][0] == "Palabra_Reservada" and todos_los_tokens[j][1] == "for":
                                    for_encontrado = True
                                    break
                                    
                            # 2. Verificar si después de 'i' hay un operador de comparación o incremento
                            operador_valido = False
                            if i+1 < len(todos_los_tokens):
                                siguiente_token = todos_los_tokens[i+1][1]
                                if siguiente_token in ['<', '>', '<=', '>=', '==', '!=', '++', '--', '+=', '-=']:
                                    operador_valido = True
                                    
                            es_variable_valida = for_encontrado and operador_valido
                            
                            # 3. O también verificar si es una declaración de variable en for
                            if not es_variable_valida and i >= 2:
                                # Verificar patrón "for (int i" o similar
                                if (todos_los_tokens[i-2][1] == "for" and 
                                    todos_los_tokens[i-1][1] == "(" and 
                                    i > 0 and todos_los_tokens[i-1][0] in ["Tipo_Dato", "Palabra_Reservada"]):
                                    es_variable_valida = True
                        
                        # Solo reportar error si no es una variable válida en este contexto
                        if not es_variable_valida:
                            errores_sintacticos.append(f"Error en Linea {num_linea}: Posible error de escritura '{token}', ¿quizás quiso decir '{palabras_similares[token]}'?")
                                
                # Analizar estructuras de control
                if tipo == "Palabra_Reservada":
                    # Validar estructura if
                    if token == "if":
                        # Guardar posición para comprobación posterior
                        if_pos = i
                        if_line = num_linea
                        
                        # Registrar este if para validar else
                        bloques_if_abiertos.append((if_line, len(llaves_apertura)))
                        
                        # Verificar formato correcto: if ( expresion ) {
                        if i + 3 < len(todos_los_tokens):
                            # Comprobar paréntesis de apertura
                            if todos_los_tokens[i+1][1] != '(':
                                errores_sintacticos.append(f"Error en Linea {num_linea}: Falta paréntesis de apertura después de 'if'")
                            
                            # Buscar el paréntesis de cierre
                            j = i + 2
                            parentesis_abiertos = 1
                            while j < len(todos_los_tokens) and parentesis_abiertos > 0:
                                if todos_los_tokens[j][1] == '(':
                                    parentesis_abiertos += 1
                                elif todos_los_tokens[j][1] == ')':
                                    parentesis_abiertos -= 1
                                j += 1
                            
                            if parentesis_abiertos > 0:
                                errores_sintacticos.append(f"Error en Linea {num_linea}: Falta paréntesis de cierre para 'if'")
                            else:
                                # Después del paréntesis de cierre debe haber una llave de apertura
                                # Buscar la llave, ignorando posibles espacios o comentarios
                                k = j
                                encontro_llave = False
                                while k < len(todos_los_tokens) and not encontro_llave:
                                    if todos_los_tokens[k][0] == "Simbolo" and todos_los_tokens[k][1] == '{':
                                        encontro_llave = True
                                        break
                                    elif todos_los_tokens[k][0] not in ["Comentario", "Espacio"]:
                                        if todos_los_tokens[k][0] == "Palabra_Reservada" and todos_los_tokens[k][1] in ["if", "else", "while", "for"]:
                                            break
                                        elif todos_los_tokens[k][1] not in ['\n', '\t', ' ']:
                                            break
                                    k += 1
                                
                                if not encontro_llave:
                                    errores_sintacticos.append(f"Error en Linea {num_linea}: Falta llave de apertura '{{' después de la condición 'if'")
                        
                        bloques_esperando_llave.append(("if", if_line))
                    
                    # Validar estructura else
                    elif token == "else":
                        else_line = num_linea
                        
                        # Verificar si hay un 'if' previo al que este else pueda corresponder
                        tiene_if_correspondiente = False
                        
                        # Un else corresponde a un if si:
                        # 1. Hay un if abierto (en bloques_if_abiertos)
                        # 2. No hay otros bloques entre el if y el else que no sean del mismo if
                        for if_line, nivel_llaves in bloques_if_abiertos:
                            # Si el nivel de llaves al momento del if es igual al actual menos 1
                            # (acabamos de cerrar una llave que corresponde al if), este else puede corresponder
                            if nivel_llaves <= len(llaves_apertura):
                                tiene_if_correspondiente = True
                                break
                        
                        if not tiene_if_correspondiente:
                            errores_sintacticos.append(f"Error en Linea {num_linea}: 'else' sin 'if' correspondiente")
                        
                        # Verificar que después del 'else' venga una llave o un 'if' (caso else if)
                        if i + 1 < len(todos_los_tokens):
                            siguiente_token = todos_los_tokens[i+1]
                            
                            # Caso else if
                            if siguiente_token[0] == "Palabra_Reservada" and siguiente_token[1] == "if":
                                pass  # El procesamiento del 'if' se hará en la siguiente iteración
                            # Caso else {
                            elif siguiente_token[1] != '{':
                                # Buscar la llave, ignorando posibles espacios o comentarios
                                k = i + 1
                                encontro_llave = False
                                while k < len(todos_los_tokens) and not encontro_llave:
                                    if todos_los_tokens[k][0] == "Simbolo" and todos_los_tokens[k][1] == '{':
                                        encontro_llave = True
                                        break
                                    elif todos_los_tokens[k][0] not in ["Comentario", "Espacio"]:
                                        if todos_los_tokens[k][1] not in ['\n', '\t', ' ']:
                                            break
                                    k += 1
                                
                                if not encontro_llave:
                                    errores_sintacticos.append(f"Error en Linea {num_linea}: Falta llave de apertura '{{' después de 'else'")
                        
                        bloques_esperando_llave.append(("else", else_line))
                    if token == "for":
                        # Guardar posición para comprobación posterior
                        for_pos = i
                        for_line = num_linea
                        
                        # Verificar formato correcto: for ( expresion ; expresion ; expresion ) {
                        if i + 3 < len(todos_los_tokens):
                            # Comprobar paréntesis de apertura
                            if todos_los_tokens[i+1][1] != '(':
                                errores_sintacticos.append(f"Error en Linea {num_linea}: Falta paréntesis de apertura después de 'for'")
                            
                            # Buscar el paréntesis de cierre y verificar la estructura interna (3 partes separadas por punto y coma)
                            j = i + 2
                            parentesis_abiertos = 1
                            punto_y_coma_count = 0
                            
                            # Variables para rastrear la posición de 'i' en un bucle for
                            posible_variable_i = None
                            
                            while j < len(todos_los_tokens) and parentesis_abiertos > 0:
                                if todos_los_tokens[j][1] == '(':
                                    parentesis_abiertos += 1
                                elif todos_los_tokens[j][1] == ')':
                                    parentesis_abiertos -= 1
                                elif todos_los_tokens[j][1] == ';' and parentesis_abiertos == 1:
                                    punto_y_coma_count += 1
                                
                                # Registrar posición de variable 'i' en el bucle for
                                if parentesis_abiertos == 1 and todos_los_tokens[j][0] == "Identificador" and todos_los_tokens[j][1] == "i":
                                    posible_variable_i = j
                                
                                j += 1
                            
                            # Excluir 'i' de las comprobaciones de errores de escritura si está en un bucle for
                            if posible_variable_i is not None:
                                # Marca la posición para que no se considere un error de escritura
                                for pos in range(posible_variable_i, posible_variable_i + 1):
                                    if pos < len(todos_los_tokens) and todos_los_tokens[pos][1] == "i":
                                        todos_los_tokens[pos] = (todos_los_tokens[pos][0], "i_variable", todos_los_tokens[pos][2])
                            
                            if parentesis_abiertos > 0:
                                errores_sintacticos.append(f"Error en Linea {num_linea}: Falta paréntesis de cierre para 'for'")
                            else:
                                # Verificar si tiene los dos punto y coma
                                if punto_y_coma_count != 2:
                                    errores_sintacticos.append(f"Error en Linea {num_linea}: La estructura 'for' debe tener 3 partes separadas por 2 punto y coma")
                                
                                # Después del paréntesis de cierre debe haber una llave de apertura
                                # Buscar la llave, ignorando posibles espacios o comentarios
                                k = j
                                encontro_llave = False
                                while k < len(todos_los_tokens) and not encontro_llave:
                                    if todos_los_tokens[k][0] == "Simbolo" and todos_los_tokens[k][1] == '{':
                                        encontro_llave = True
                                        break
                                    elif todos_los_tokens[k][0] not in ["Comentario", "Espacio"]:
                                        if todos_los_tokens[k][0] == "Palabra_Reservada" and todos_los_tokens[k][1] in ["if", "else", "while", "for"]:
                                            break
                                        elif todos_los_tokens[k][1] not in ['\n', '\t', ' ']:
                                            break
                                    k += 1
                                
                                if encontro_llave:
                                    # Si encontramos la llave, no añadimos a bloques_esperando_llave
                                    pass
                                else:
                                    errores_sintacticos.append(f"Error en Linea {num_linea}: Falta llave de apertura '{{' después de la declaración 'for'")
                                    # Solo añadimos a bloques_esperando_llave si no encontramos la llave
                        bloques_esperando_llave.append(("for", for_line))
                        
                    # Validaciones para while, for, switch, etc.
                    elif token in ["while", "for", "switch", "do"]:
                        bloques_esperando_llave.append((token, num_linea))
                        # Aquí se puede añadir validaciones específicas para cada estructura
                
                # Verificar apertura de bloques
                elif tipo == "Simbolo" and token == '{':
                    # Determinar el contexto de esta llave
                    contexto = "desconocido"
                    if bloques_esperando_llave:
                        tipo_bloque, linea_bloque = bloques_esperando_llave.pop()
                        contexto = tipo_bloque
                    
                    # Guardar posición y contexto de la llave
                    llaves_apertura.append((num_linea, contexto))
                    ambitos.append(set())
                
                # Verificar cierre de bloques
                elif tipo == "Simbolo" and token == '}':
                    if llaves_apertura:
                        linea_apertura, contexto = llaves_apertura.pop()
                        
                        # Si estamos cerrando un bloque if, actualizar bloques_if_abiertos
                        if contexto == "if":
                            # Buscar y eliminar el if correspondiente
                            for j in range(len(bloques_if_abiertos)-1, -1, -1):
                                if_line, nivel = bloques_if_abiertos[j]
                                if nivel == len(llaves_apertura) + 1:  # +1 porque ya hemos hecho pop
                                    bloques_if_abiertos.pop(j)
                                    break
                        
                        if ambitos:
                            ambitos.pop()
                    else:
                        errores_sintacticos.append(f"Error en Linea {num_linea}: Llave de cierre '}}' sin llave de apertura correspondiente")
                
                i += 1
            
            # Verificar si quedaron llaves de apertura sin cerrar
            if llaves_apertura:
                for num_linea, contexto in llaves_apertura:
                    errores_sintacticos.append(f"Error en Linea {num_linea}: Llave de apertura '{{' en bloque '{contexto}' sin llave de cierre correspondiente")
            
            # Verificar si quedaron estructuras esperando llaves
            if bloques_esperando_llave:
                for tipo_bloque, num_linea in bloques_esperando_llave:
                    errores_sintacticos.append(f"Error en Linea {num_linea}: Estructura '{tipo_bloque}' sin llave de apertura correspondiente")
            
            return todos_los_tokens_procesados, errores_sintacticos
        
        # Realizar post-procesamiento
        todos_los_tokens_procesados, errores_sintacticos = post_procesar_tokens()
        
        # Traducir el código
        def traducir_codigo(tokens):
            """
            Traduce el código utilizando los tokens procesados.
            """
            codigo_traducido = []
            linea_actual = []
            
            for item in tokens_y_formato:
                if isinstance(item, str):  # Es indentación o nueva línea
                    if '\n' in item:
                        if linea_actual:
                            codigo_traducido.append(''.join(linea_actual))
                            linea_actual = []
                        codigo_traducido.append('')  # Línea vacía
                    else:
                        linea_actual.append(item)
                else:  # Es un token
                    tipo, token, _ = item
                    if tipo == "Palabra_Reservada":
                        token = PALABRAS_RESERVADAS.get(token, token)
                    linea_actual.append(token)
            
            if linea_actual:  # Procesar última línea si existe
                codigo_traducido.append(''.join(linea_actual))
            
            return '\n'.join(codigo_traducido)
        
        # Guardar solo los tokens en trad.txt (sin sus tipos)
        tokens_para_archivo = []
        for tipo, valor, _ in todos_los_tokens:
            if tipo != "Comentario":  # Opcional: ignorar comentarios en trad.txt
                tokens_para_archivo.append(valor)
        
        with open("trad.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(tokens_para_archivo))
        
        # Generar y guardar código traducido
        codigo_traducido = traducir_codigo(tokens_y_formato)
        with open("traduccion.txt", "w", encoding="utf-8") as f:
            f.write(codigo_traducido)
        
        # Guardar errores
        todos_los_errores = errores_lexicos + errores_sintacticos
        
        with open("errores.txt", "w", encoding="utf-8") as f:
            if todos_los_errores:
                f.write("\n".join(todos_los_errores))
            else:
                f.write("No se encontraron errores léxicos ni sintácticos.")
        
        print("Análisis léxico, sintáctico y traducción completados correctamente usando PLY.")

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
