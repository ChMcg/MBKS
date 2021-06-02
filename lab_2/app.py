from functools import reduce
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt as QtConstants
import string
import json
from lab_3.AccessControlMatrix import AccessControlMatrix as ACM

class Validator(QtCore.QObject):
    maitrix_updated = QtCore.pyqtSignal()

    def __init__(self, matrix: dict[str, set]):
        super().__init__()
        if len(matrix.keys()) == 0:
            raise ValueError("Пустая матрица доступа")
        self.matrix = matrix
    
    def validate(self, user: str, raw_str: str) -> str:
        if user not in self.matrix.keys():
            return ''
        ret = "".join([x for x in raw_str if x in self.matrix[user] ])
        print(f"{user}: '{raw_str}' -> '{ret}'")
        return ret
    
    def users(self) -> int:
        return len(self.get_users())

    def count_users(self) -> int:
        return len(self.get_users())

    def get_all_chars(self) -> list[str]:
        if len(self.matrix) > 0:
            return sorted(list(reduce(lambda x,y: {*x, *y}, self.matrix.values())))
        else:
            return ""

    def get_users(self) -> list[str]:
        return self.matrix.keys()
    
    def get_available_chars_for_user(self, user: str) -> set:
        return self.matrix[user]

    def add_symbol(self, user: str, sybmol: str):
        self.matrix[user].add(sybmol)
        
    def add_symbol_for_user(self, user: str, sybmol: str):
        self.matrix[user].add(sybmol)
        self.maitrix_updated.emit()

    def remove_symbol(self, user: str, sybmol: str):
        self.matrix[user].remove(sybmol)
        self.maitrix_updated.emit()

    def add_user(self, user: str):
        if not user in self.matrix.keys():
            self.matrix[user] = set()
            self.maitrix_updated.emit()

    def remove_user(self, user: str):
        if user in self.matrix.keys():
            del self.matrix[user]
            self.maitrix_updated.emit()

    def save_state(self, path: str):
        with open(path, 'w') as f:
            state = dict()
            for user in self.get_users():
                state[user] = ''.join(self.matrix[user])
            f.write(json.dumps(state, indent=2))
            f.close()
    
    def load_state(self, path: str):
        with open(path, 'r') as f:
            self.matrix = dict()
            state: dict = json.loads(f.read())
            for user in state.keys():
                self.matrix[user] = set(state[user])
            self.maitrix_updated.emit()


class SettingsTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setup_ui()
        self._alphabet = string.ascii_lowercase
        # self._cb_table: dict[tuple, QtWidgets.QCheckBox] = {}
        self._cb_table: dict[int, tuple[str, str]] = {}

    def setup_ui(self):
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._table = QtWidgets.QTableWidget(self)
        self._table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # self._table.horizontalHeader().setSectionResizeMode()
        self._table.itemChanged.connect(self.handle_item_checked_new)
        self._layout.addWidget(self._table)
        self.add_user_menu()
        self.add_char_menu()

    def add_user_menu(self):
        self._add_user_widget = QtWidgets.QWidget(self)
        self._add_user_layout = QtWidgets.QHBoxLayout(self._add_user_widget)
        self._add_user_widget.setLayout(self._add_user_layout)
        self._leUser = QtWidgets.QLineEdit()
        self._pbAddUser = QtWidgets.QPushButton("Добавить пользователя")
        self._pbAddUser.clicked.connect(self.handle_add_user)
        self._pbRemoveUser = QtWidgets.QPushButton("Удалить пользователя")
        self._pbRemoveUser.clicked.connect(self.handle_remove_user)
        self._add_user_layout.addWidget(self._leUser)
        self._add_user_layout.addWidget(self._pbAddUser)
        self._add_user_layout.addWidget(self._pbRemoveUser)
        self._layout.addWidget(self._add_user_widget)

    def add_char_menu(self):
        self._add_chars_widget = QtWidgets.QWidget(self)
        self._add_chars_layout = QtWidgets.QHBoxLayout(self._add_chars_widget)
        self._add_chars_widget.setLayout(self._add_chars_layout)
        self._leChars = QtWidgets.QLineEdit()
        self._pbAddChar = QtWidgets.QPushButton("Добавить сивмолы")
        self._pbAddChar.clicked.connect(self.handle_add_chars)
        self._pbRemoveChar = QtWidgets.QPushButton("Удалить символы")
        self._pbRemoveChar.clicked.connect(self.handle_add_chars)
        self._add_chars_layout.addWidget(self._leChars)
        self._add_chars_layout.addWidget(self._pbAddChar)
        self._add_chars_layout.addWidget(self._pbRemoveChar)
        self._layout.addWidget(self._add_chars_widget)

    def set_validator(self, validator: Validator):
        self._validator = validator
        self._validator.maitrix_updated.connect(self.handle_matrix_updated)
        self._alphabet = self._validator.get_all_chars()
        self.update_table()
    
    def update_table(self):
        # self._table.setRowCount(self._validator.users())
        # self._table.setColumnCount(len(self._alphabet))
        # for i, user in enumerate(self._validator.get_users()):
        #     item = QtWidgets.QTableWidgetItem(user)
        #     self._table.setVerticalHeaderItem(i, item)
        # for k, char in enumerate(self._alphabet):
        #     item = QtWidgets.QTableWidgetItem(char)
        #     self._table.setHorizontalHeaderItem(k, item)
        # for i, user in enumerate(self._validator.get_users()):
        #     for k, char in enumerate(self._alphabet):
        #         widget = QtWidgets.QWidget(self)
        #         layout = QtWidgets.QVBoxLayout()
        #         widget.setLayout(layout)
        #         cb = QtWidgets.QCheckBox()
        #         if char in self._validator.get_available_chars_for_user(user):
        #             cb.setChecked(True)
        #         layout.addWidget(cb)
        #         layout.setContentsMargins(0,0,0,0)
        #         layout.setAlignment(QtCore.Qt.AlignCenter)
        #         self._table.setCellWidget(i, k, widget)
        #         self._cb_table[id(cb)] = (user, char)
        #         cb.stateChanged.connect(lambda state: self.handle_item_checked(state))
        self._table.blockSignals(True)
        self._table.clear()
        self._cb_table.clear()
        self._table.setRowCount(self._validator.count_users())
        self._table.setColumnCount(len(self._alphabet))
        for i, user in enumerate(self._validator.get_users()):
            v_header_item = QtWidgets.QTableWidgetItem(user)
            self._table.setVerticalHeaderItem(i, v_header_item)
            for k, char in enumerate(self._alphabet):
                if i == 0:
                    h_header_item = QtWidgets.QTableWidgetItem(char)
                    self._table.setHorizontalHeaderItem(k, h_header_item)
                cell_item = QtWidgets.QTableWidgetItem('')
                cell_item.setFlags(QtConstants.ItemIsUserCheckable | QtConstants.ItemIsEnabled)
                if char in self._validator.get_available_chars_for_user(user):
                    cell_item.setCheckState(QtConstants.Checked)
                else:
                    cell_item.setCheckState(QtConstants.Unchecked)
                cell_item.setData(QtConstants.UserRole, (user, char))
                self._table.setItem(i,k, cell_item)
        self._table.blockSignals(False)

    def handle_item_checked_new(self, item: QtWidgets.QTableWidgetItem):
        # self._validator.blockSignals(True)
        user, char = item.data(QtConstants.UserRole)
        checked = item.checkState() == QtConstants.Checked
        print((user, char), '->', checked)
        if checked:
            self._validator.add_symbol_for_user(user, char)
        else:
            self._validator.remove_symbol(user, char)
        # self._validator.blockSignals(False)
    
    def handle_item_checked(self, state: int):
        user, char = self._cb_table[id(self.sender())]
        if state == QtCore.Qt.Checked:
            self._validator.add_symbol(user, char)
        elif state == QtCore.Qt.Unchecked:
            self._validator.remove_symbol(user, char)

    def handle_add_user(self, user: str):
        user = self._leUser.text()
        self._validator.add_user(user)
    
    def handle_remove_user(self, user: str):
        user = self._leUser.text()
        self._validator.remove_user(user)

    def handle_add_chars(self):
        chars = self._leChars.text()
        for char in chars:
            if not char in self._alphabet:
                self._alphabet += char
                self._alphabet = "".join(sorted(list(set(self._alphabet))))
        self.update_table()

    def handle_remove_chars(self):
        chars = self._leChars.text()
        for char in chars:
            if char in self._alphabet:
                self._alphabet = self._alphabet.replace(char, '')
        self.update_table()

    def handle_matrix_updated(self):
        # self.set_validator(self._validator)
        self._alphabet = self._validator.get_all_chars()
        self.update_table()
    
        

class InputTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self._cbUser = QtWidgets.QComboBox(self)
        self._leInput = QtWidgets.QLineEdit(self)
        self._leFormatted = QtWidgets.QLineEdit(self)
        self._leFormatted.setEnabled(False)
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.addWidget(self._cbUser)
        self._layout.addWidget(self._leInput)
        self._layout.addWidget(self._leFormatted)
        self._leInput.textChanged.connect(self.handle_text_changed)
        self._cbUser.currentIndexChanged.connect(self.handle_user_change)
        self._layout.setAlignment(QtConstants.AlignTop)

    def set_validator(self, validator: Validator):
        self._validator = validator
        self._cbUser.clear()
        self._cbUser.addItems(validator.matrix.keys())
        self._current_user = list(validator.matrix.keys())[0]
        self._validator.maitrix_updated.connect(self.handle_matrix_updated)

    def handle_user_change(self):
        self._current_user = self._cbUser.currentText()
        self.handle_text_changed(self._leInput.text())
    
    def handle_text_changed(self, text: str):
        if not hasattr(self, "_current_user"):
            return
        formatted = self._validator.validate(self._current_user, text)
        self._leFormatted.setText(formatted)

    def handle_matrix_updated(self):
        self._cbUser.clear()
        self._cbUser.addItems(self._validator.matrix.keys())
        self._current_user = list(self._validator.matrix.keys())[0]
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setup_ui()
        self.validator = Validator({'default': {'a','b','c'}, 'other': {'d','e','f'}})
        self._input_tab.set_validator(self.validator)
        self._settings_tab.set_validator(self.validator)
        try:
            with open('matrix.json'):
                self.validator.load_state('matrix.json')
        except Exception as e:
            print('no state found')
        self.validator.maitrix_updated.connect(self.save_state)
        self.setMinimumSize(QtCore.QSize(600, 500))

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
        print('saving')
        self.validator.save_state("matrix.json")


class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')

    def exec(self):
        window = MainWindow(self)
        window.show()
        return super().exec()
