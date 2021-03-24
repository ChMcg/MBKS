from lab_3.AccessControlMatrix import AccessControlMatrix
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt as QtConstants


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
