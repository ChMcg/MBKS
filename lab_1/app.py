import time
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

"""
    написать две проги: 
    - одна записывает файл в какую-то папку, 
    - другая отслеживает изменения в этой папке и копирует новые файлы из этой папки через буфер обмена в другую папку
"""

source_path = "./test/source"
target_path = "./test/target"
font        = "arial"
font_size   = 13


class Handler(FileSystemEventHandler, QtCore.QObject):
    file_created = QtCore.pyqtSignal(str)

    def __init__(self, observer: Observer = None):
        super(QtCore.QObject, self).__init__()
        self.observer = observer or None

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory:
            self.file_created.emit(event.src_path)


class FsObserver(QtCore.QThread):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self._observer = Observer()
        self._handler = Handler()
        self._observer.schedule(self._handler, path=source_path, recursive=True)
    
    def run(self) -> None:
        self._observer.start()
        while True:
            time.sleep(1)


class Writer(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setup_ui()
        self._pbCreateFile.clicked.connect(self.create_file)

    def setup_ui(self):
        self.setFont(QtGui.QFont(font, font_size))
        self._widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self._widget)
        self._leFileName = QtWidgets.QLineEdit(self)
        self._pbCreateFile = QtWidgets.QPushButton("Создать файл")
        self._layout = QtWidgets.QHBoxLayout()
        self._widget.setLayout(self._layout)
        self._layout.addWidget(self._leFileName)
        self._layout.addWidget(self._pbCreateFile)

    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()

    def create_file(self):
        file_name = self._leFileName.text()
        with open(f"{source_path}/{file_name}", 'w') as f:
            f.write("")


class Reader(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setup_ui()
        self._observer = FsObserver()
        self._observer._handler.file_created.connect(self.handle_file_creation)
        self._observer.start()

    def setup_ui(self):
        self.setFont(QtGui.QFont(font, font_size))
        self._table = QtWidgets.QListWidget(self)
        self.setCentralWidget(self._table)

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
        target_file = f"{target_path}/{file_name}"
        with open(target_file, 'w') as target:
            target.write(file_data)
        self.log_to_ui(f"{source_file} -> {target_file}")

    def log_to_ui(self, msg: str):
        self._table.addItem(msg)


class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')

    def exec(self):
        reader = Reader()
        reader.show()
        writer = Writer()
        writer.show()
        return super().exec()


if __name__ == '__main__':
    App().exec()
