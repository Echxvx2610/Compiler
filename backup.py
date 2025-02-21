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
        self.compileMenu = self.menuBar.addMenu("Compile")
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
        self.analizerAction = self.create_action("Analyze Content", "resources/img/inverted/triangulo.png", self.analize_content)
        self.newTerminal = self.create_action("New Terminal", "resources/img/inverted/comando.png", self.new_terminal)

        # Agregar acciones al menú
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.exitAction)

        self.compileMenu.addAction(self.analizerAction)
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
        """Analiza el contenido del editor línea por línea y muestra los resultados en la terminal."""

        content = self.textEdit.toPlainText()  # Obtener el texto completo del editor
        lines = content.splitlines()  # Dividir el contenido en líneas

        # Palabras reservadas de C
        palabras_reservadas_C = [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", 
            "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", 
            "restrict", "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", 
            "union", "unsigned", "void", "volatile", "while", "_Alignas", "_Alignof", "_Atomic", 
            "_Bool", "_Complex", "_Generic", "_Imaginary", "_Noreturn", "_Static_assert", "_Thread_local"
        ]

        # Expresiones regulares para los diferentes elementos
        identificador_regex = r'\b[A-Za-z_][A-Za-z0-9_]*\b'
        numero_regex = r'\b\d+\.\d+|\b\d+\b'  # para enteros y decimales
        comentario_unilinea_regex = r'//.*'  # Comentarios de una sola línea
        comentario_multibloque_regex = r'/\*.*?\*/'  # Comentarios multibloque
        cadena_regex = r'"[^"]*"'
        caracter_regex = r"'[^']*'"
        simbolo_regex = r'[!+<>=#\[\]{}();,.-]'  # Incluye los símbolos comunes en C
        libreria_regex = r'\b[A-Za-z_][A-Za-z0-9_]*\.h\b'  # Captura librerías .h

        # Función para detectar caracteres no imprimibles en texto
        def detectar_caracteres_no_imprimibles(texto):
            r"""Detecta caracteres no imprimibles y los muestra como su código ASCII en formato \xNN."""
            return ''.join([f'\\x{ord(c):02x}' if ord(c) < 32 or ord(c) > 126 else c for c in texto])

        # Recorrer cada línea del contenido
        for line in lines:
            self.terminal.append(f"Análisis de línea: {line}")
            
            # Buscar y procesar los comentarios
            comentarios_unilinea = re.findall(comentario_unilinea_regex, line)
            comentarios_multibloque = re.findall(comentario_multibloque_regex, line)
            
            # Procesar los comentarios de una sola línea y multibloque
            comentarios = comentarios_unilinea + comentarios_multibloque  # Combina los dos tipos de comentarios

            # Detectar los caracteres no imprimibles en los comentarios y las cadenas
            ascii_detectados_comentarios = []
            for comment in comentarios:
                ascii_detectados_comentarios.extend([f'\\x{ord(c):02x}' for c in comment if ord(c) < 32 or ord(c) > 126])

            # Eliminar los comentarios para evitar que interfieran con el análisis de otros elementos
            line_sin_comentarios = re.sub(comentario_unilinea_regex, '', line)
            line_sin_comentarios = re.sub(comentario_multibloque_regex, '', line_sin_comentarios)  # Eliminar comentarios multibloque
            
            # Encontrar los diferentes elementos en la línea
            identificadores = re.findall(identificador_regex, line_sin_comentarios)
            numeros = re.findall(numero_regex, line_sin_comentarios)
            cadenas = re.findall(cadena_regex, line_sin_comentarios)
            caracteres = re.findall(caracter_regex, line_sin_comentarios)
            simbolos = re.findall(simbolo_regex, line_sin_comentarios)
            librerias = re.findall(libreria_regex, line_sin_comentarios)

            # Filtrar identificadores reservados
            identificadores_reservados = [word for word in identificadores if word in palabras_reservadas_C]
            identificadores_funciones = [ident for ident in identificadores if f"{ident}()" in line_sin_comentarios]

            # Lista para almacenar los caracteres ASCII no imprimibles detectados en cadenas
            ascii_detectados_cadenas = []
            for cadena in cadenas:
                ascii_detectados_cadenas.extend([f'\\x{ord(c):02x}' for c in cadena if ord(c) < 32 or ord(c) > 126])

            # Mostrar resultados solo si la categoría tiene elementos
            if simbolos:
                self.terminal.append("  - Simbolos:")
                for sym in simbolos:
                    self.terminal.append(f"    - {sym}")

            if identificadores:
                self.terminal.append("  - Identificadores:")
                for ident in identificadores:
                    if ident not in palabras_reservadas_C:
                        self.terminal.append(f"    - {ident}")

            if identificadores_reservados:
                self.terminal.append("  - Palabras reservadas:")
                for word in identificadores_reservados:
                    self.terminal.append(f"    - {word}")

            if identificadores_funciones:
                self.terminal.append("  - Funciones:")
                for func in identificadores_funciones:
                    self.terminal.append(f"    - {func}()")

            if librerias:
                self.terminal.append("  - Librerías:")
                for lib in librerias:
                    self.terminal.append(f"    - {lib}")

            if numeros:
                self.terminal.append("  - Números:")
                for num in numeros:
                    self.terminal.append(f"    - {num}")

            if comentarios:
                self.terminal.append("  - Comentarios:")
                for comment in comentarios:
                    self.terminal.append(f"    - {comment}")

            if cadenas:
                self.terminal.append("  - Cadenas:")
                for string in cadenas:
                    # Detectar caracteres no imprimibles en las cadenas también
                    string = detectar_caracteres_no_imprimibles(string)
                    self.terminal.append(f"    - {string}")

            if caracteres:
                self.terminal.append("  - Caracteres:")
                for char in caracteres:
                    # Detectar caracteres no imprimibles en los caracteres también
                    char = detectar_caracteres_no_imprimibles(char)
                    self.terminal.append(f"    - {char}")

            # Mostrar ASCII detectados en comentarios y cadenas, si hay
            if ascii_detectados_comentarios or ascii_detectados_cadenas:
                self.terminal.append("  - ASCII:")
                # Mostrar los ASCII detectados de los comentarios
                for ascii_char in ascii_detectados_comentarios:
                    self.terminal.append(f"    - {ascii_char}")
                # Mostrar los ASCII detectados de las cadenas
                for ascii_char in ascii_detectados_cadenas:
                    self.terminal.append(f"    - {ascii_char}")

        print("Contenido analizado línea por línea y mostrado en la terminal.")







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
