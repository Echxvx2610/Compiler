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
        FUNCIONES_BIBLIOTECA = ["printf", "main"]
        
        # Variables globales para el seguimiento
        errores_lexicos = []
        errores_sintacticos = []
        todos_los_tokens = []
        tokens_y_formato = []
        variables_declaradas = {}  # {nombre: tipo}
        funciones_declaradas = set()
        
        # Definir tokens (requerido por PLY)
        tokens = [
            'PALABRA_RESERVADA',
            'TIPO_DATO', 
            'IDENTIFICADOR',
            'ENTERO',
            'DECIMAL',
            'CADENA',
            'CADENA_ERROR',
            'CARACTER',
            'CARACTER_ERROR',
            'LIBRERIA',
            'LIBRERIA_PERSONALIZADA',
            'COMENTARIO_LINEA',
            'COMENTARIO_BLOQUE',
            'SIMBOLO',
            'NEWLINE'
        ]
        
        # Estados del lexer
        states = (
            ('comentario', 'exclusive'),
        )
        
        # Reglas de tokens (deben seguir el patrón t_NOMBRE)
        
        # Comentarios de línea
        def t_COMENTARIO_LINEA(t):
            r'//.*'
            todos_los_tokens.append(('Comentario', t.value, t.lineno))
            return t
        
        # Comentarios de bloque - inicio
        def t_COMENTARIO_BLOQUE_INICIO(t):
            r'/\*'
            t.lexer.comentario_inicio = t.lineno
            t.lexer.comentario_texto = t.value
            t.lexer.begin('comentario')

        # Reglas para el estado de comentario
        def t_comentario_contenido(t):
            r'[^*\n]+'
            t.lexer.comentario_texto += t.value

        def t_comentario_asterisco(t):
            r'\*(?!/)'
            t.lexer.comentario_texto += t.value

        def t_comentario_newline(t):
            r'\n+'
            t.lexer.lineno += len(t.value)
            t.lexer.comentario_texto += t.value

        def t_comentario_fin(t):
            r'\*/'
            t.lexer.comentario_texto += t.value
            t.type = 'COMENTARIO_BLOQUE'
            t.value = t.lexer.comentario_texto
            t.lineno = t.lexer.comentario_inicio
            t.lexer.begin('INITIAL')
            todos_los_tokens.append(('Comentario', t.value, t.lineno))
            return t

        def t_comentario_error(t):
            errores_lexicos.append(f"Error en comentario línea {t.lineno}: carácter inesperado '{t.value[0]}'")
            t.lexer.skip(1)
        
        # Bibliotecas (deben ir antes que las cadenas)
        def t_LIBRERIA(t):
            r'<[a-zA-Z_][a-zA-Z0-9_]*\.h>'
            todos_los_tokens.append(('Libreria', t.value, t.lineno))
            return t
        
        def t_LIBRERIA_PERSONALIZADA(t):
            r'"[a-zA-Z_][a-zA-Z0-9_]*\.h"'
            todos_los_tokens.append(('Libreria_Personalizada', t.value, t.lineno))
            return t
        
        # Cadenas (deben ir después de las librerías)
        def t_CADENA(t):
            r'"([^"\\]|\\.)*"'
            todos_los_tokens.append(('Cadena', t.value, t.lineno))
            return t
        
        def t_CADENA_ERROR(t):
            r'"([^"\\]|\\.)*$'
            errores_lexicos.append(f"Error línea {t.lineno}: Cadena sin cerrar: {t.value}")
            todos_los_tokens.append(('Cadena_Error', t.value, t.lineno))
            return t
        
        # Caracteres
        def t_CARACTER(t):
            r"'([^'\\]|\\.)'"
            todos_los_tokens.append(('Caracter', t.value, t.lineno))
            return t
        
        def t_CARACTER_ERROR(t):
            r"'([^'\\]|\\.)*'?"
            if not t.value.endswith("'") or len(t.value.replace("\\", "")) > 3:
                errores_lexicos.append(f"Error línea {t.lineno}: Carácter mal formado: {t.value}")
                todos_los_tokens.append(('Caracter_Error', t.value, t.lineno))
            return t
        
        # Números decimales (debe ir antes que enteros)
        def t_DECIMAL(t):
            r'\d+\.\d+'
            todos_los_tokens.append(('Decimal', float(t.value), t.lineno))
            return t
        
        # Números enteros
        def t_ENTERO(t):
            r'\d+'
            todos_los_tokens.append(('Entero', int(t.value), t.lineno))
            return t
        
        # Identificadores y palabras clave
        def t_IDENTIFICADOR(t):
            r'[a-zA-Z_][a-zA-Z0-9_]*'
            # Clasificar el token
            if t.value in PALABRAS_RESERVADAS:
                t.type = 'PALABRA_RESERVADA'
                todos_los_tokens.append(('Palabra_Reservada', t.value, t.lineno))
            elif t.value in TIPOS_DATOS:
                t.type = 'TIPO_DATO'
                todos_los_tokens.append(('Tipo_Dato', t.value, t.lineno))
            else:
                todos_los_tokens.append(('Identificador', t.value, t.lineno))
            return t
        
        # Símbolos y operadores
        def t_SIMBOLO(t):
            r'[#<>(){};,.+\-*/=\[\]!&|%^~?:]'
            todos_los_tokens.append(('Simbolo', t.value, t.lineno))
            return t
        
        # Saltos de línea
        def t_NEWLINE(t):
            r'\n+'
            t.lexer.lineno += len(t.value)
            # No agregamos saltos de línea a la lista de tokens
            pass
        
        # Espacios y tabs (ignorar)
        t_ignore = ' \t'
        
        # Manejo de errores
        def t_error(t):
            errores_lexicos.append(f"Error línea {t.lineno}: Carácter ilegal '{t.value[0]}'")
            t.lexer.skip(1)
        
        def post_procesar_tokens(tokens_list):
            """
            Post-procesa la lista de tokens para detectar errores sintácticos
            """
            nonlocal errores_sintacticos, variables_declaradas, funciones_declaradas
            
            tokens_procesados = []
            i = 0
            
            # PASO 1: Análisis previo - recopilar todas las declaraciones sin validar
            declaraciones_encontradas = {}
            
            # Debug: Imprimir todos los tokens para diagnóstico
            print("DEBUG - Tokens encontrados:")
            for j, (tipo, valor, linea) in enumerate(tokens_list):
                print(f"  {j}: {tipo} -> '{valor}' (línea {linea})")
            
            for j in range(len(tokens_list)):
                tipo, valor, linea = tokens_list[j]
                
                # Detectar declaraciones de variables sin validar sintaxis aún
                if tipo == 'Tipo_Dato' and j + 1 < len(tokens_list):
                    next_token = tokens_list[j + 1]
                    if next_token[0] == 'Identificador':
                        print(f"DEBUG - Declaración encontrada: {next_token[1]} tipo {valor}")
                        declaraciones_encontradas[next_token[1]] = valor
                        variables_declaradas[next_token[1]] = valor  # Agregar inmediatamente
                
                # Detectar declaraciones de funciones
                if tipo == 'Identificador' and j + 1 < len(tokens_list):
                    if tokens_list[j + 1][0] == 'Simbolo' and tokens_list[j + 1][1] == '(':
                        # Verificar si hay un tipo de dato antes (declaración de función)
                        if j > 0 and tokens_list[j-1][0] == 'Tipo_Dato':
                            funciones_declaradas.add(valor)
                            print(f"DEBUG - Función declarada: {valor}")
                        elif valor == 'main':
                            funciones_declaradas.add(valor)
                            print(f"DEBUG - Función main encontrada: {valor}")
            
            # Agregar funciones de biblioteca como conocidas
            for func in FUNCIONES_BIBLIOTECA:
                funciones_declaradas.add(func)
            
            print(f"DEBUG - Variables declaradas encontradas: {variables_declaradas}")
            print(f"DEBUG - Funciones declaradas encontradas: {funciones_declaradas}")
            
            # PASO 2: Procesar tokens con información completa
            while i < len(tokens_list):
                tipo, valor, linea = tokens_list[i]
                
                # Detectar declaraciones de variables
                if tipo == 'Tipo_Dato':
                    if i + 1 < len(tokens_list) and tokens_list[i + 1][0] == 'Identificador':
                        var_name = tokens_list[i + 1][1]
                        # No sobreescribir si ya está declarada
                        if var_name not in variables_declaradas:
                            variables_declaradas[var_name] = valor
                        
                        print(f"DEBUG - Procesando declaración: {var_name} = {valor}")
                        
                        # Verificar punto y coma solo si no es parámetro de función
                        if not es_parametro_funcion(tokens_list, i):
                            punto_coma_encontrado = False
                            j = i + 2
                            
                            # Buscar hasta encontrar ; 
                            while j < len(tokens_list):
                                if tokens_list[j][0] == 'Simbolo':
                                    if tokens_list[j][1] == ';':
                                        punto_coma_encontrado = True
                                        break
                                    elif tokens_list[j][1] in ['{', '}', ')', ',']:
                                        break
                                j += 1
                            
                            if not punto_coma_encontrado and not es_declaracion_en_for(tokens_list, i):
                                errores_sintacticos.append(f"Error sintáctico línea {linea}: Falta ';' después de la declaración de '{var_name}'")
                
                # Detectar funciones
                elif tipo == 'Identificador':
                    if i + 1 < len(tokens_list) and tokens_list[i + 1][0] == 'Simbolo' and tokens_list[i + 1][1] == '(':
                        # Es una función
                        if valor == 'main':
                            tokens_procesados.append(('Main_Function', valor, linea))
                        elif valor in FUNCIONES_BIBLIOTECA:
                            tokens_procesados.append(('Llamada_Funcion_Biblioteca', valor, linea))
                            print(f"DEBUG - Función de biblioteca encontrada: {valor}")
                            # Verificar paréntesis balanceados
                            if not verificar_parentesis_balanceados(tokens_list, i + 1):
                                errores_sintacticos.append(f"Error sintáctico línea {linea}: Paréntesis desbalanceados en función '{valor}'")
                        else:
                            # Determinar si es declaración o llamada
                            if es_declaracion_funcion(tokens_list, i):
                                tokens_procesados.append(('Declaracion_Funcion', valor, linea))
                            else:
                                if valor in funciones_declaradas:
                                    tokens_procesados.append(('Llamada_Funcion', valor, linea))
                                else:
                                    tokens_procesados.append(('Llamada_Funcion_No_Declarada', valor, linea))
                                    errores_sintacticos.append(f"Error sintáctico línea {linea}: Función '{valor}' no declarada")
                                
                                if not verificar_parentesis_balanceados(tokens_list, i + 1):
                                    errores_sintacticos.append(f"Error sintáctico línea {linea}: Paréntesis desbalanceados en función '{valor}'")
                    else:
                        # Verificar si la variable está declarada
                        print(f"DEBUG - Verificando variable: {valor}")
                        print(f"DEBUG - Variables conocidas: {list(variables_declaradas.keys())}")
                        print(f"DEBUG - Declaraciones encontradas: {list(declaraciones_encontradas.keys())}")
                        
                        if (valor not in variables_declaradas and 
                            valor not in declaraciones_encontradas and 
                            valor not in funciones_declaradas and 
                            valor not in FUNCIONES_BIBLIOTECA):
                            errores_sintacticos.append(f"Error sintáctico línea {linea}: Variable '{valor}' no declarada")
                        
                        # Si está en declaraciones_encontradas, agregarla a variables_declaradas
                        if valor in declaraciones_encontradas and valor not in variables_declaradas:
                            variables_declaradas[valor] = declaraciones_encontradas[valor]
                        
                        tokens_procesados.append((tipo, valor, linea))
                
                # Verificar punto y coma en sentencias de control
                elif tipo == 'Palabra_Reservada' and valor in ['return', 'break', 'continue']:
                    tokens_procesados.append((tipo, valor, linea))
                    if not verificar_punto_coma_siguiente(tokens_list, i):
                        errores_sintacticos.append(f"Error sintáctico línea {linea}: Falta ';' después de '{valor}'")
                
                else:
                    tokens_procesados.append((tipo, valor, linea))
                
                i += 1
            
            return tokens_procesados
        
        def es_parametro_funcion(tokens_list, index):
            """Verifica si la declaración está dentro de parámetros de función"""
            # Buscar hacia atrás hasta encontrar un paréntesis de apertura
            i = index - 1
            nivel_parentesis = 0
            
            while i >= 0:
                if tokens_list[i][0] == 'Simbolo':
                    if tokens_list[i][1] == ')':
                        nivel_parentesis += 1
                    elif tokens_list[i][1] == '(':
                        nivel_parentesis -= 1
                        if nivel_parentesis < 0:
                            # Estamos dentro de paréntesis, verificar si es función
                            if i > 0 and tokens_list[i-1][0] == 'Identificador':
                                return True
                            return False
                    elif tokens_list[i][1] in [';', '{', '}'] and nivel_parentesis == 0:
                        return False
                i -= 1
            return False
        
        def es_declaracion_en_for(tokens_list, index):
            """Verifica si la declaración está dentro de un bucle for"""
            # Buscar hacia atrás la palabra 'for'
            i = index - 1
            nivel_parentesis = 0
            
            while i >= 0:
                if tokens_list[i][0] == 'Simbolo':
                    if tokens_list[i][1] == ')':
                        nivel_parentesis += 1
                    elif tokens_list[i][1] == '(':
                        nivel_parentesis -= 1
                        if nivel_parentesis < 0 and i > 0:
                            if tokens_list[i-1][0] == 'Palabra_Reservada' and tokens_list[i-1][1] == 'for':
                                return True
                            return False
                i -= 1
            return False
        
        def es_declaracion_funcion(tokens_list, index):
            """Determina si es una declaración de función"""
            # Buscar hacia atrás un tipo de dato
            i = index - 1
            while i >= 0:
                if tokens_list[i][0] == 'Tipo_Dato':
                    return True
                elif tokens_list[i][0] == 'Simbolo' and tokens_list[i][1] in ['\n', ';', '}', '{']:
                    break
                i -= 1
            return False
        
        def verificar_parentesis_balanceados(tokens_list, start_index):
            """Verifica que los paréntesis estén balanceados"""
            if start_index >= len(tokens_list) or tokens_list[start_index][1] != '(':
                return False
            
            nivel = 1
            i = start_index + 1
            
            while i < len(tokens_list) and nivel > 0:
                if tokens_list[i][0] == 'Simbolo':
                    if tokens_list[i][1] == '(':
                        nivel += 1
                    elif tokens_list[i][1] == ')':
                        nivel -= 1
                i += 1
            
            return nivel == 0
        
        def verificar_punto_coma_siguiente(tokens_list, index):
            """Verifica que haya un punto y coma después de la sentencia"""
            i = index + 1
            while i < len(tokens_list):
                if tokens_list[i][0] == 'Simbolo':
                    if tokens_list[i][1] == ';':
                        return True
                    elif tokens_list[i][1] in ['{', '}']:
                        return False
                i += 1
            return False
        
        def detectar_errores_estructurales():
            """Detecta errores de llaves, paréntesis y corchetes desbalanceados"""
            nivel_llaves = 0
            nivel_parentesis = 0
            nivel_corchetes = 0
            
            for tipo, valor, linea in todos_los_tokens:
                if tipo == 'Simbolo':
                    if valor == '{':
                        nivel_llaves += 1
                    elif valor == '}':
                        nivel_llaves -= 1
                        if nivel_llaves < 0:
                            errores_sintacticos.append(f"Error sintáctico línea {linea}: Llave de cierre sin apertura")
                    elif valor == '(':
                        nivel_parentesis += 1
                    elif valor == ')':
                        nivel_parentesis -= 1
                        if nivel_parentesis < 0:
                            errores_sintacticos.append(f"Error sintáctico línea {linea}: Paréntesis de cierre sin apertura")
                    elif valor == '[':
                        nivel_corchetes += 1
                    elif valor == ']':
                        nivel_corchetes -= 1
                        if nivel_corchetes < 0:
                            errores_sintacticos.append(f"Error sintáctico línea {linea}: Corchete de cierre sin apertura")
            
            # Verificar elementos sin cerrar
            if nivel_llaves > 0:
                errores_sintacticos.append(f"Error sintáctico: {nivel_llaves} llave(s) sin cerrar")
            if nivel_parentesis > 0:
                errores_sintacticos.append(f"Error sintáctico: {nivel_parentesis} paréntesis sin cerrar")
            if nivel_corchetes > 0:
                errores_sintacticos.append(f"Error sintáctico: {nivel_corchetes} corchete(s) sin cerrar")
        
        # Crear el lexer
        try:
            lexer = lex.lex()
            lexer.lineno = 1
        except Exception as e:
            print(f"Error creando lexer: {e}")
            return None
        
        # Obtener contenido del editor
        contenido = self.textEdit.toPlainText()
        
        # Analizar el contenido
        lexer.input(contenido)
        
        # Procesar todos los tokens
        while True:
            tok = lexer.token()
            if not tok:
                break
        
        # Post-procesar tokens
        tokens_procesados = post_procesar_tokens(todos_los_tokens)
        
        # Detectar errores estructurales
        detectar_errores_estructurales()
        
        # Generar archivos de salida
        try:
            # 1. Archivo trad.txt - Solo tokens
            with open('trad.txt', 'w', encoding='utf-8') as f:
                for tipo, valor, linea in tokens_procesados:
                    f.write(f"{valor}\n")
            
            # 2. Archivo traduccion.txt - Código traducido
            with open('traduccion.txt', 'w', encoding='utf-8') as f:
                for tipo, valor, linea in tokens_procesados:
                    if tipo == 'Palabra_Reservada' and valor in PALABRAS_RESERVADAS:
                        f.write(f"{PALABRAS_RESERVADAS[valor]} ")
                    else:
                        f.write(f"{valor} ")
            
            # 3. Archivo errores.txt - Todos los errores
            with open('errores.txt', 'w', encoding='utf-8') as f:
                f.write("=== ANÁLISIS DE ERRORES ===\n\n")
                
                f.write("ERRORES LÉXICOS:\n")
                if errores_lexicos:
                    for error in errores_lexicos:
                        f.write(f"  • {error}\n")
                else:
                    f.write("  ✓ No se encontraron errores léxicos\n")
                
                f.write(f"\nERRORES SINTÁCTICOS:\n")
                if errores_sintacticos:
                    for error in errores_sintacticos:
                        f.write(f"  • {error}\n")
                else:
                    f.write("  ✓ No se encontraron errores sintácticos\n")
                
                f.write(f"\n=== RESUMEN ===\n")
                f.write(f"Total errores léxicos: {len(errores_lexicos)}\n")
                f.write(f"Total errores sintácticos: {len(errores_sintacticos)}\n")
                f.write(f"Variables declaradas: {len(variables_declaradas)}\n")
                f.write(f"Funciones encontradas: {len(funciones_declaradas)}\n")
                
                if variables_declaradas:
                    f.write(f"\nVARIABLES DECLARADAS:\n")
                    for var, tipo in variables_declaradas.items():
                        f.write(f"  • {var}: {tipo}\n")
                
                if funciones_declaradas:
                    f.write(f"\nFUNCIONES ENCONTRADAS:\n")
                    for func in funciones_declaradas:
                        f.write(f"  • {func}\n")
            
            print("✓ Análisis completado exitosamente")
            print(f"✓ Archivos generados: trad.txt, traduccion.txt, errores.txt")
            print(f"✓ Errores encontrados: {len(errores_lexicos) + len(errores_sintacticos)}")
            
            return {
                'tokens': tokens_procesados,
                'errores_lexicos': errores_lexicos,
                'errores_sintacticos': errores_sintacticos,
                'variables': variables_declaradas,
                'funciones': funciones_declaradas
            }
            
        except Exception as e:
            print(f"Error generando archivos: {e}")
            return None
        
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
