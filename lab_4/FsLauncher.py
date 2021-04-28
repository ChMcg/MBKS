from fuse import FUSE
import sys
from PyQt5 import Qt, QtCore, QtWidgets

from lab_4.SecureFS import SecureFS
from lab_4.other import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)



class FsLauncher(QtCore.QThread):
    path: str = "mount"
    fg: bool = True
    allow_other: bool = True

    def __init__(self, path: str, fg: bool = True, allow_other: bool = True) -> None:
        super().__init__()
        self.path = path
        self.fg = fg
        self.allow_other = allow_other
        self.fs = SecureFS()

    def run(self) -> None:
        FUSE(
                self.fs, 
                self.path, 
                foreground=self.fg, 
                allow_other=self.allow_other
            )
