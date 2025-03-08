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
        Analiza el contenido del editor línea por línea y genera dos archivos:
        - trad.txt: Análisis detallado del código (solo tokens)
        - traduccion.c: Código C traducido al español
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

        def clasificar_token(token, siguiente_token=None):
            """Clasifica un token y retorna su tipo y valor."""
            if token.startswith('//') or token.startswith('/*'):
                return "Comentario", token
            elif token in PALABRAS_RESERVADAS:
                return "Palabra Reservada", token
            elif token.endswith('.h') and not token.startswith('"'):
                return "Libreria", token
            elif token.startswith('"') and token.endswith('.h"'):
                return "Libreria Personalizada", token
            elif token in SIMBOLOS:
                return "Simbolo", token
            elif token.startswith('"') or token.startswith("'"):
                return "Cadena", token
            elif token.replace('.', '').isdigit():
                return "Numero", token
            elif siguiente_token == '(':
                return "Identificador de Funcion", token
            else:
                return "Identificador", token



        def procesar_linea(linea, en_comentario_bloque, comentario_acumulado):
            """
            Procesa una línea de código y retorna sus tokens clasificados.
            También maneja el estado de los comentarios de bloque.
            """
            # Si estamos en un comentario de bloque, buscamos el cierre
            if en_comentario_bloque:
                if '*/' in linea:
                    # Encontramos el final del comentario
                    parte_final = linea[:linea.index('*/') + 2]
                    comentario_acumulado += '\n' + parte_final
                    en_comentario_bloque = False
                    return [("Comentario", comentario_acumulado)], False, ""
                else:
                    # Continuamos en el comentario
                    comentario_acumulado += '\n' + linea
                    return [], True, comentario_acumulado

            # Buscar comentarios de bloque en la línea actual
            if '/*' in linea and '*/' not in linea:
                inicio = linea.index('/*')
                en_comentario_bloque = True
                comentario_acumulado = linea[inicio:]
                
                # Procesar la parte antes del comentario
                linea_antes = linea[:inicio]
                if linea_antes.strip():
                    token_regex = r'(//.*|".*?"|\'.*?\'|\b[A-Za-z_][A-Za-z0-9_]*\.h\b|\b[A-Za-z_][A-Za-z0-9_]*\b|\b\d+\.\d+|\b\d+\b|[!#\\+<>=\[\]{}();,.-])'
                    tokens_antes = [(clasificar_token(t.strip(), siguiente=None)[0], t.strip()) 
                                  for t in re.findall(token_regex, linea_antes) if t.strip()]
                    return tokens_antes, True, comentario_acumulado
                return [], True, comentario_acumulado

            # Procesar línea normal
            token_regex = r'(//.*|/\*.*?\*/|".*?"|\'.*?\'|\b[A-Za-z_][A-Za-z0-9_]*\.h\b|\b[A-Za-z_][A-Za-z0-9_]*\b|\b\d+\.\d+|\b\d+\b|[!#\\+<>=\[\]{}();,.-])'
            tokens = re.findall(token_regex, linea)
            tokens = [t.strip() for t in tokens if t.strip()]
            
            resultados = []
            for i, token in enumerate(tokens):
                siguiente = tokens[i + 1] if i + 1 < len(tokens) else None
                if '/*' in token and '*/' in token:  # Comentario de bloque en una línea
                    resultados.append(("Comentario", token))
                else:
                    tipo, valor = clasificar_token(token, siguiente)
                    resultados.append((tipo, valor))
            
            return resultados, False, ""

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
                    tipo, token = item
                    if tipo == "Palabra Reservada":
                        token = PALABRAS_RESERVADAS.get(token, token)
                    linea_actual.append(token)
            
            if linea_actual:  # Procesar última línea si existe
                codigo_traducido.append(" ".join(linea_actual))
            
            return "\n".join(codigo_traducido)

        # Obtener el contenido del editor
        contenido = self.textEdit.toPlainText()
        lineas = contenido.splitlines()
        
        # Para almacenar tokens y formato para la traducción
        tokens_y_formato = []
        # Para almacenar solo los tokens para trad.txt
        tokens_para_archivo = []
        
        # Variables para manejar comentarios de bloque
        en_comentario_bloque = False
        comentario_acumulado = ""
        
        # Procesar cada línea
        for linea in lineas:
            indentacion = " " * (len(linea) - len(linea.lstrip()))
            tokens_y_formato.append(indentacion)
            
            if not linea.strip():
                continue
            
            tokens, en_comentario_bloque, comentario_acumulado = procesar_linea(
                linea, en_comentario_bloque, comentario_acumulado
            )
            
            if tokens:  # Si hay tokens en la línea
                tokens_y_formato.extend(tokens)
                # Agregar tokens al archivo trad.txt
                for tipo, valor in tokens:
                    tokens_para_archivo.append(f"{tipo}: {valor}")
                tokens_para_archivo.append("")  # Línea vacía entre líneas de código
        
        # Guardar análisis en trad.txt (solo tokens)
        with open("trad.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(tokens_para_archivo).rstrip())
        
        # Generar y guardar código traducido
        codigo_traducido = traducir_codigo(tokens_y_formato)
        with open("traduccion.txt", "w", encoding="utf-8") as f:
            f.write(codigo_traducido)
        
        print("Análisis y traducción completados correctamente.")

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=options)
        
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
