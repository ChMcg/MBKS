from lab_3.AccessControlMatrix import AccessControlMatrix
from lab_3.InputTab import InputTab
from lab_3.SettingsTab import SettingsTab        

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt as QtConstants


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setup_ui()
        self.matrix = AccessControlMatrix({})
        self._input_tab.set_validator(self.matrix)
        self._settings_tab.set_matrix(self.matrix)
        self.matrix.add_user('default', '12345')
        try:
            with open('matrix.json'):
                self.matrix.load_state('matrix.json')
        except Exception as e:
            print('no state found')
        self.matrix.maitrix_updated.connect(self.save_state)
        self.matrix.user_added.emit()

    def setup_ui(self):
        self._tab_wigdet = QtWidgets.QTabWidget(self)
        self._settings_tab = SettingsTab(self)
        self._input_tab = InputTab(self)
        self._tab_wigdet.addTab(self._settings_tab, "Настройки")
        self._tab_wigdet.addTab(self._input_tab,    "Ввод")
        self.setCentralWidget(self._tab_wigdet)

    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()

    def save_state(self):
        self.matrix.save_state('matrix.json')

class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')

    def exec(self):
        window = MainWindow(self)
        window.show()
        return super().exec()
