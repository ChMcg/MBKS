from lab_3.AccessControlMatrix import AccessControlMatrix
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint, Qt as QtConstants
import string


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
        self._table.setSelectionMode(QtWidgets.QTableWidget.NoSelection)
        self._table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self._layout.addWidget(self._table)
        self.add_create_section(self._layout)
        self.add_remove_section(self._layout)
        self.add_grant_section(self._layout)

    def add_create_section(self, layout: QtWidgets.QLayout):
        self._w_create_gb = QtWidgets.QGroupBox("Create", self)
        create_gb_layout = QtWidgets.QHBoxLayout(self._w_create_gb)
        self._w_create_gb.setLayout(create_gb_layout)
        self._cbb_create_user = QtWidgets.QComboBox(self)
        self._cbb_create_user.setEditable(True)
        self._cbb_create_user.setMinimumWidth(150)
        create_gb_layout.addWidget(self._cbb_create_user)
        self._le_create_chars = QtWidgets.QLineEdit(self)
        create_gb_layout.addWidget(self._le_create_chars)
        self._pb_create = QtWidgets.QPushButton("Добавить", self)
        create_gb_layout.addWidget(self._pb_create)
        layout.addWidget(self._w_create_gb)
        self._pb_create.clicked.connect(self.handle_create)

    def add_remove_section(self, layout: QtWidgets.QLayout):
        self._w_remove_gb = QtWidgets.QGroupBox("Remove", self)
        remove_gb_layout = QtWidgets.QHBoxLayout(self._w_remove_gb)
        self._w_remove_gb.setLayout(remove_gb_layout)
        self._cbb_remove_user = QtWidgets.QComboBox(self)
        self._cbb_remove_user.setMinimumWidth(150)
        self._cbb_remove_user.setEditable(False)
        remove_gb_layout.addWidget(self._cbb_remove_user)
        self._le_remove_chars = QtWidgets.QLineEdit(self)
        remove_gb_layout.addWidget(self._le_remove_chars)
        self._pb_remove = QtWidgets.QPushButton("Удалить", self)
        remove_gb_layout.addWidget(self._pb_remove)
        layout.addWidget(self._w_remove_gb)
        self._w_remove_gb.setEnabled(False)
        self._pb_remove.clicked.connect(self.handle_remove)

    def add_grant_section(self, layout: QtWidgets.QLayout):
        self._w_gb_grant = QtWidgets.QGroupBox("Grant", self)
        grant_gb_layout = QtWidgets.QHBoxLayout(self._w_gb_grant)
        self._w_gb_grant.setLayout(grant_gb_layout)
        self._cbb_grant_user_1 = QtWidgets.QComboBox(self)
        self._cbb_grant_user_1.setMinimumWidth(100)
        self._cbb_grant_user_1.setEditable(False)
        grant_gb_layout.addWidget(self._cbb_grant_user_1)
        self._cbb_grant_user_2 = QtWidgets.QComboBox(self)
        self._cbb_grant_user_2.setMinimumWidth(100)
        self._cbb_grant_user_2.setEditable(False)
        grant_gb_layout.addWidget(self._cbb_grant_user_2)
        self._le_grant_chars = QtWidgets.QLineEdit(self)
        grant_gb_layout.addWidget(self._le_grant_chars)
        self._pb_grant = QtWidgets.QPushButton("Передать", self)
        grant_gb_layout.addWidget(self._pb_grant)
        layout.addWidget(self._w_gb_grant)
        self._pb_grant.clicked.connect(self.handle_grant)

    def set_matrix(self, matrix: AccessControlMatrix):
        self._matrix = matrix
        self._matrix.maitrix_updated.connect(self.handle_matrix_updated)
        self._matrix.user_added.connect(self.handle_matrix_updated)
        self._matrix.user_added.connect(self.handle_users_updated)
        self._matrix.user_removed.connect(self.handle_matrix_updated)
        self._matrix.user_removed.connect(self.handle_users_updated)
        self._alphabet = self._matrix.get_all_chars()
        self.update_table()

    def handle_matrix_updated(self):
        self._alphabet = self._matrix.get_all_chars()
        self.update_table()

    def handle_users_updated(self):
        users = self._matrix.get_users()
        self._cbb_create_user.clear()
        self._cbb_remove_user.clear()
        self._cbb_grant_user_1.clear()
        self._cbb_grant_user_2.clear()
        if len(users) > 0:
            self._cbb_create_user.addItems(users)
            self._cbb_create_user.setEditText("")
            self._cbb_remove_user.addItems(users)
            self._cbb_grant_user_1.addItems(users)
            self._cbb_grant_user_2.addItems(users)
            self.set_users_available(True)
        else:
            self.set_users_available(False)
    
    def set_users_available(self, available: bool):
        self._w_remove_gb.setEnabled(available)
        self._w_gb_grant.setEnabled(available)

    def update_table(self):
        self._table.setRowCount(self._matrix.count_users())
        self._table.setColumnCount(len(self._alphabet))
        for i, user in enumerate(self._matrix.get_users()):
            item = QtWidgets.QTableWidgetItem(user)
            self._table.setVerticalHeaderItem(i, item)
        for k, char in enumerate(self._alphabet):
            item = QtWidgets.QTableWidgetItem(char)
            self._table.setHorizontalHeaderItem(k, item)
        for i, user in enumerate(self._matrix.get_users()):
            for k, char in enumerate(self._alphabet):
                widget = QtWidgets.QWidget(self)
                layout = QtWidgets.QVBoxLayout()
                widget.setLayout(layout)
                cb = QtWidgets.QCheckBox()
                if char in self._matrix.get_available_chars_for_user(user):
                    cb.setChecked(True)
                layout.addWidget(cb)
                layout.setContentsMargins(0,0,0,0)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                self._table.setCellWidget(i, k, widget)
                self._cb_table[id(cb)] = (user, char)
                cb.stateChanged.connect(lambda state: self.handle_item_checked(state))

    def handle_item_checked(self, state: int):
        user, char = self._cb_table[id(self.sender())]
        if state == QtCore.Qt.Checked:
            self._matrix.add_symbol_for_user(user, char)
        elif state == QtCore.Qt.Unchecked:
            self._matrix.remove_symbol(user, char)

    def handle_create(self):
        user = self._cbb_create_user.currentText()
        chars = self._le_create_chars.text()
        self._matrix.create(user, chars)
    
    def handle_remove(self):
        user = self._cbb_remove_user.currentText()
        chars = self._le_remove_chars.text()
        self._matrix.remove(user, chars)

    def handle_grant(self):
        user_1 = self._cbb_grant_user_1.currentText()
        user_2 = self._cbb_grant_user_2.currentText()
        chars = self._le_grant_chars.text()
        self._matrix.grant(user_1, user_2, chars)

    # def handle_add_user(self, user: str):
    #     user = self._leUser.text()
    #     self._matrix.add_user(user)
    
    # def handle_remove_user(self, user: str):
    #     user = self._leUser.text()
    #     self._matrix.remove_chars_for_user(user)

    # def handle_add_chars(self):
    #     chars = self._leChars.text()
    #     for char in chars:
    #         if not char in self._alphabet:
    #             self._alphabet += char
    #             self._alphabet = "".join(sorted(list(set(self._alphabet))))
    #     self.update_table()

    # def handle_remove_chars(self):
    #     chars = self._leChars.text()
    #     for char in chars:
    #         if char in self._alphabet:
    #             self._alphabet = self._alphabet.replace(char, '')
    #     self.update_table()

    def handle_matrix_updated(self):
        self.set_matrix(self._matrix)
        

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

    def set_validator(self, validator: AccessControlMatrix):
        self._validator = validator
        self._cbUser.clear()
        self._cbUser.addItems(validator.matrix.keys())
        # self._current_user = list(validator.matrix.keys())[0]
        self._cbUser.currentText()
        self._validator.user_added.connect(self.handle_matrix_updated)
        self._validator.user_removed.connect(self.handle_matrix_updated)

    def handle_user_change(self):
        self._current_user = self._cbUser.currentText()
        if self._current_user != "":
            self.handle_text_changed(self._leInput.text())
    
    def handle_text_changed(self, text: str):
        if not hasattr(self, "_current_user") or self._current_user == "":
            return
        formatted = self._validator.validate(self._current_user, text)
        self._leFormatted.setText(formatted)

    def handle_matrix_updated(self):
        self._cbUser.clear()
        self._cbUser.addItems(self._validator.matrix.keys())
        self._cbUser.currentText()
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setup_ui()
        # self.validator = AccessControlMatrix({'default': {'a','b','c'}, 'other': {'d','e','f'}})
        self.matrix = AccessControlMatrix({})
        self._input_tab.set_validator(self.matrix)
        self._settings_tab.set_matrix(self.matrix)
        self.matrix.add_user('default', '12345')

    def setup_ui(self):
        self._tab_wigdet = QtWidgets.QTabWidget(self)
        self._settings_tab = SettingsTab(self)
        self._input_tab = InputTab(self)
        self._tab_wigdet.addTab(self._settings_tab, "Настройки")
        self._tab_wigdet.addTab(self._input_tab,    "Ввод")
        self.setCentralWidget(self._tab_wigdet)
        self.setGeometry(QtCore.QRect(QPoint(0,0), QPoint(600, 600)))
        # self.setFixedSize(600, 600)

    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()


class App(Qt.QApplication):
    def __init__(self, argv=[]) -> None:
        super().__init__(argv)
        self.setStyle('Fusion')

    def exec(self):
        window = MainWindow(self)
        window.show()
        return super().exec()
