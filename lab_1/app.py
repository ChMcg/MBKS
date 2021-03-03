import time
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

"""
    написать две проги: 
    - одна записывает файл в какую-то папку, 
    - другая отслеживает изменения в этой папке и копирует новые файлы из этой папки через буфер обмена в другую папку
"""

safe_path    = "./test/user_safe"
unsafe_path  = "./test/user_unsafe"
villian_path = "./test/villain_safe"
font         = "arial"
font_size    = 12

ID_FORMAT     = '[%Y-%m-%d_%H:%M:%S]'
ID_FORMAT_TMP = '%Y-%m-%d_%H-%M-%S'

def timestamp() -> str:
    return time.strftime(ID_FORMAT, time.localtime())

def timestamp_for_file() -> str:
    return time.strftime(ID_FORMAT_TMP, time.localtime())


class Handler(FileSystemEventHandler, QtCore.QObject):
    file_created = QtCore.pyqtSignal(str)

    def __init__(self, observer: Observer = None):
        super(QtCore.QObject, self).__init__()
        self.observer = observer or None

    def on_modified(self, event):
        if not event.is_directory:
            self.file_created.emit(event.src_path)


class FsObserver(QtCore.QThread):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self._observer = Observer()
        self._handler = Handler()
        self._observer.schedule(self._handler, path=unsafe_path, recursive=True)
    
    def run(self) -> None:
        self._observer.start()
        while True:
            time.sleep(1)


class Writer(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setup_ui()
        self._pbCreateFile.clicked.connect(self.create_private_file)
        self._pbCopyToPublic.clicked.connect(self.create_public_file)

    def setup_ui(self):
        self.setFont(QtGui.QFont(font, font_size))
        self._widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self._widget)
        self._leFileName = QtWidgets.QLineEdit(self)
        self._pbCreateFile = QtWidgets.QPushButton("Сохранить приватно")
        self._layout = QtWidgets.QVBoxLayout()
        self._widget.setLayout(self._layout)
        self._buttons_layout = QtWidgets.QHBoxLayout()
        self._layout.addLayout(self._buttons_layout)
        self._buttons_layout.addWidget(self._leFileName)
        self._buttons_layout.addWidget(self._pbCreateFile)
        self._pbCopyToPublic = QtWidgets.QPushButton("Скопировать в открытую директорию", self)
        self._layout.addWidget(self._pbCopyToPublic)
        self._text_edit = QtWidgets.QTextEdit(self)
        self._layout.addWidget(self._text_edit)

    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()

    def create_private_file(self):
        file_name = self._leFileName.text()
        with open(f"{safe_path}/{file_name}", 'w') as f:
            f.write(self._text_edit.toPlainText())

    def create_public_file(self):
        file_name = self._leFileName.text()
        with open(f"{unsafe_path}/{file_name}", 'w') as f:
            f.write(self._text_edit.toPlainText())


class Reader(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setup_ui()
        self._observer = FsObserver()
        self._observer._handler.file_created.connect(self.handle_file_creation)
        self._observer.start()
        self.resize(QtCore.QSize(750, 250))

    def setup_ui(self):
        self.setFont(QtGui.QFont(font, font_size))
        self._table = QtWidgets.QListWidget(self)
        self._text_browser = QtWidgets.QTextBrowser(self)
        self.setCentralWidget(self._text_browser)

    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()

    def handle_file_creation(self, source_file: str):
        self.copy_file(source_file)

    def copy_file(self, source_file: str):
        file_data = ""
        with open(source_file, 'r') as source:
            file_data = source.read()
        file_name = source_file.split('/')[-1]
        self.log_to_ui(f"Обнаружено сохранение: {file_name}")
        target_file = f"{villian_path}/{timestamp_for_file()}_{file_name}"
        with open(target_file, 'w') as target:
            target.write(file_data)
        self.log_to_ui(f"Скопирован файл: {target_file}")

    def log_to_ui(self, msg: str):
        self._text_browser.append(f"{timestamp()} {msg}")


class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')

    def exec(self):
        writer = Writer()
        writer.show()
        return super().exec()

class VillainApp(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')

    def exec(self):
        reader = Reader()
        reader.show()
        return super().exec()

if __name__ == '__main__':
    App().exec()
