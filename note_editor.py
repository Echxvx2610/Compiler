from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtPrintSupport import *
import sys

class LineNumberArea(QWidget):
    def __init__(self, text_edit):
        super().__init__(text_edit)
        self.text_edit = text_edit

        # Hacer que el área de números de línea sea transparente y del tamaño adecuado
        self.setStyleSheet("background: rgba(0, 0, 0, 0);")
        self.setFixedWidth(50)  # Ancho fijo para los números

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))  # Color blanco para los números
        painter.setFont(self.font())

        block = self.text_edit.document().firstBlock()
        block_number = 1

        # Dibujar los números de línea
        while block.isValid():
            rect = self.text_edit.document().documentLayout().blockBoundingRect(block)
            painter.drawText(0, rect.top(), self.width(), rect.height(), Qt.AlignRight, str(block_number))
            block = block.next()
            block_number += 1

class NoteEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Establecer icono de la ventana
        self.setWindowIcon(QIcon("resources/img/compilador.png"))

        # Definir variables
        self.title = "Notas"
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()

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
        self.newAction = self.create_action("New File", "resources/img/agregar-archivo.png", self.new_content)
        self.openAction = self.create_action("Open File", "resources/img/abrir-documento.png", self.load_content)
        self.saveAction = self.create_action("Save File", "resources/img/disquete.png", self.save_content)
        self.saveAsAction = self.create_action("Save As File", "resources/img/guardar-el-archivo.png", self.save_content_as)
        self.exitAction = self.create_action("Exit Application", "resources/img/cerrar-sesion.png", self.close)
        self.analizerAction = self.create_action("Analyze Content", "resources/img/triangulo.png", self.analize_content)
        self.newTerminal = self.create_action("New Terminal", "resources/img/comando.png", self.new_terminal)

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

        # Crear un QTextEdit para la edición de notas
        self.textEdit = QTextEdit(self)
        self.setCentralWidget(self.textEdit)

        # Crear y agregar el área de números de línea
        self.lineNumberArea = LineNumberArea(self.textEdit)
        self.textEdit.setViewportMargins(self.lineNumberArea.width(), 0, 0, 0)

        # Conectar la señal textChanged para actualizar el área de números de línea
        self.textEdit.textChanged.connect(self.update_line_numbers)

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
                print("QSS cargado correctamente:\n", stylesheet)  # Debug
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error cargando stylesheet: {e}")

    def apply_frosted_glass_effect(self):
        """Aplica un efecto de vidrio esmerilado (Frosted Glass)."""
        # Establecer la transparencia de la ventana
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)  # Reduce la opacidad para simular el efecto de "vidrio"

        # Aplicar desenfoque a un widget (puedes aplicar esto a otros widgets también)
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(10)  # Controla el desenfoque
        self.textEdit.setGraphicsEffect(blur_effect)  # Aplica el desenfoque al QTextEdit

    def update_line_numbers(self):
        """Actualiza el área de números de línea después de que se cambie el texto."""
        self.lineNumberArea.update()

    # Declaración de funciones
    def new_content(self):
        print("Contenido creado...")

    def save_content(self):
        print("Contenido guardado...")

    def save_content_as(self):
        print("Contenido guardado como...")

    def load_content(self):
        print("Contenido cargado...")

    def analize_content(self):
        print("Contenido analizado...")

    def new_terminal(self):
        print("Nueva terminal abierta...")

if __name__ == '__main__':
    application = QApplication(sys.argv)
    editor = NoteEditor()
    sys.exit(application.exec())
