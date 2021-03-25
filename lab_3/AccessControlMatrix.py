from PyQt5 import QtCore
from functools import reduce
import json

class AccessControlMatrix(QtCore.QObject):
    maitrix_updated = QtCore.pyqtSignal()
    user_added = QtCore.pyqtSignal()
    user_removed = QtCore.pyqtSignal()

    def __init__(self, matrix: dict[str, set]):
        super().__init__()
        # if len(matrix.keys()) == 0:
        #     raise ValueError("Пустая матрица доступа")
        self.matrix = matrix
    
    def validate(self, user: str, raw_str: str) -> str:
        ret = "".join([x for x in raw_str if x in self.matrix[user] ])
        print(f"{user}: '{raw_str}' -> '{ret}'")
        return ret
    
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

    def add_symbol_for_user(self, user: str, sybmol: str):
        self.matrix[user].add(sybmol)
        
    def remove_symbol(self, user: str, sybmol: str):
        self.matrix[user].remove(sybmol)

    def add_user(self, user: str, symbol: str):
        if not user in self.matrix.keys():
            self.matrix[user] = set(symbol)
            self.user_added.emit()
        else:
            self.matrix[user] |= set(symbol)
        self.maitrix_updated.emit()

    def remove_chars_for_user(self, user: str, symbol: str):
        changed = False
        if user in self.matrix.keys():
            for char in symbol:
                if char in self.matrix[user]:
                    self.matrix[user].remove(char)
                    changed = True
            if len(self.matrix[user]) == 0:
                del self.matrix[user]
                self.user_removed.emit()
        if changed:
            self.maitrix_updated.emit()

    def grant(self, user_1: str, user_2: str, symbol: str):
        changed = False
        if user_1 in self.matrix.keys() and user_2 in self.matrix.keys():
            for char in symbol:
                if char in self.matrix[user_1]:
                    self.matrix[user_2].add(char)
                    changed = True
        if changed:
            self.maitrix_updated.emit()
    
    def create(self, user: str, symbol: str):
        return self.add_user(user, symbol)

    def remove(self, user: str, symbol: str):
        return self.remove_chars_for_user(user, symbol)

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
