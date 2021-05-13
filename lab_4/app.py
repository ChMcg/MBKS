#!/home/inelos/projects/MBKS/venv/bin/python

from logging import log
from lab_4.SecureFS import SecureFS
from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from fuse import FUSE
import sys
import time
from PyQt5 import Qt, QtCore, QtWidgets
import typing

# from lab_4.Memory import Memory
# from lab_4.SecureFS import SecureFS
from lab_4.FsLauncher import FsLauncher
from lab_4.Fs import User, Level
from lab_4.other import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Users(QtWidgets.QWidget):
    def __init__(self, fs: SecureFS, parent) -> None:
        super().__init__(parent)
        self._fs = fs
        print("fs_id:", id(self._fs))
        self.setup_ui()

    def setup_ui(self):
        self._main_widget = QtWidgets.QWidget()
        self._fs.users_updated.connect(self.update_users)
        self.update_users()
    
    def update_users(self):
        del self._main_widget
        print('updating', self._fs.users.items())
        self._main_widget = QtWidgets.QWidget(self)
        self._layout = QtWidgets.QVBoxLayout(self._main_widget)
        self.setLayout(self._layout)
        self._main_widget.setLayout(self._layout)
        for uid, user in self._fs.users.items():
            # user: User = user
            print('adding user:', (uid, user))
            new_item = QtWidgets.QWidget(self)
            layout = QtWidgets.QHBoxLayout(new_item)
            new_item.setLayout(layout)
            label = QtWidgets.QLabel(user.login)
            cbox = QtWidgets.QComboBox()
            for level in Level.all_levels():
                cbox.addItem(level, uid)
            cbox.currentIndexChanged.connect(self.update_user_level)
            cbox.setCurrentIndex(user.access_level)
            layout.addWidget(label)
            layout.addWidget(cbox)
            self._layout.addWidget(new_item)
    
    def update_user_level(self, index: int):
        cbox: QtWidgets.QComboBox = self.sender()
        uid = cbox.currentData()
        level = cbox.currentText()
        level = Level.from_str(level)
        self._fs.set_user_level(uid, level)




class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, fs: SecureFS, parent):
        super().__init__()
        self.fs = fs
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
        self._log.setWordWrap(True)
        self.show_log("Приложение запущено")
        self._tw = QtWidgets.QTabWidget(self)
        self.setCentralWidget(self._tw)
        # self.setCentralWidget(self._log)
        self._users_tab = Users(self.fs, self)
        self._tw.addTab(self._users_tab, "Users")
        self._tw.addTab(self._log, "Log")

    
    def subscribe_to_fs(self, fs_object: SecureFS):
        fs_object.s_log.connect(self.show_log)
        fs_object.s_warning.connect(self.show_warning)
        pass
    
    def show_log(self, message: str):
        self.show_message("log", message, '#FFFFFF')

    def show_warning(self, message: str):
        self.show_message("warning", message, '#FFCDD2')

    def show_message(self, tag: str, message: str, color: str):
        t = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        padding = self._tag_padding
        intro = f"{t} [{tag:>7}]:"
        wi = QtWidgets.QListWidgetItem(f"{intro} {message}")
        wi.setBackground(QColor(color))
        self._log.addItem(wi)
        self._log.scrollToBottom()


    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()


class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')
        self.setFont(QtGui.QFont("monospace", 10))
        self.fsl = FsLauncher("mount")
        print("fs_id:", id(self.fsl.fs))


    def exec(self):
        window = MainWindow(self.fsl.fs, self)
        window.subscribe_to_fs(self.fsl.fs)
        self.fsl.fs.scan_users()
        self.fsl.fs.create_default_dirs()
        self.fsl.start()
        window.show()
        return super().exec()


def main():
    # FUSE(Memory(), "mount", foreground=True, allow_other=True)
    # FUSE(SecureFS(), "mount", foreground=True, allow_other=True)
    App().exec()
    


if __name__ == '__main__':
    main()