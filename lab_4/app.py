#!/home/inelos/projects/MBKS/venv/bin/python

from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from fuse import FUSE
import sys
import time
from PyQt5 import Qt, QtCore, QtWidgets

# from lab_4.Memory import Memory
# from lab_4.SecureFS import SecureFS
from lab_4.FsLauncher import FsLauncher
from lab_4.other import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)





class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        possible_tags: list[str] = [
            'log',
            'info',
            'warning'
        ]
        self._tag_padding = max([len(x) for x in possible_tags])
        self._log = QtWidgets.QListWidget(self)
        self._log.setSelectionMode(QtWidgets.QListWidget.NoSelection)
        self.setCentralWidget(self._log)
        self.show_log("Приложение запущено")
        self.show_warning("Кто-то творит хуету")
    
    def show_log(self, message: str):
        self.show_message("log", message, '#FFFFFF')

    def show_warning(self, message: str):
        self.show_message("warning", message, '#FFCDD2')

    def show_message(self, tag: str, message: str, color: str):
        t = time.strftime('%Y-%m-%d_%H:%M', time.localtime())
        padding = self._tag_padding
        intro = f"{t} [{tag:>7}]:"
        wi = QtWidgets.QListWidgetItem(f"{intro} {message}")
        wi.setBackground(QColor(color))
        self._log.addItem(wi)


    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()


class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')
        self.setFont(QtGui.QFont("monospace"))
        self.fsl = FsLauncher("mount")

    def exec(self):
        self.fsl.start()
        window = MainWindow(self)
        window.show()
        return super().exec()


def main():
    # FUSE(Memory(), "mount", foreground=True, allow_other=True)
    # FUSE(SecureFS(), "mount", foreground=True, allow_other=True)
    App().exec()
    


if __name__ == '__main__':
    main()