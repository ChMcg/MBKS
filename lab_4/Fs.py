from __future__ import annotations
from os import access
from pydantic import BaseModel
import stat
from time import time
from enum import Enum

class Stat(BaseModel):
    st_ino:   int = 0
    st_dev:   int = 0
    st_mode:  int = 0o664
    st_nlink: int = 0
    st_uid:   int = 0
    st_gid:   int = 0
    st_size:  int = 0
    st_atime: int = 0
    st_mtime: int = 0
    st_ctime: int = 0


class Level(int, Enum):
    NonSecret   = 0
    Secret      = 1
    TopSecret   = 2

    def to_str(self) -> str:
        tmp = {
            Level.NonSecret: "NonSecret",
            Level.Secret: "Secret",
            Level.TopSecret: "TopSecret"
        }
        return tmp[self]


class User(BaseModel):
    st_uid: int = 1000
    st_gid: int = 1000
    access_level: Level = Level.NonSecret


class FsEntity(BaseModel):
    st: Stat = Stat()
    name: str
    level: Level = Level.NonSecret

    def is_dir(self) -> bool:
        return self.st.st_mode & stat.S_IFDIR


class File(FsEntity):
    data: bytes = b''

    def __init__(self, name: str, data: bytes, user: User, **kwargs):
        super().__init__(name=name, **kwargs)
        self.st = Stat(**{'st_gid': user.st_gid, 'st_uid': user.st_uid})
        self.st.st_ctime = self.st.st_atime = self.st.st_mtime = int(time())
        self.st.st_size = len(data)
        self.st.st_mode |= stat.S_IFREG
        self.st.st_nlink = 1
        self.data = data


class Dir(FsEntity):
    child: dict[str, FsEntity] = {}

    def __init__(self, name: str, user: User, **kwargs):
        super().__init__(name=name, **kwargs)
        self.st = Stat(**{'st_gid': user.st_gid, 'st_uid': user.st_uid})
        self.st.st_ctime = self.st.st_atime = self.st.st_mtime = int(time())
        self.st.st_mode |= stat.S_IFDIR
        self.st.st_nlink = 2
        self.st.st_size = 4096
    
    def add_child(self, file: FsEntity):
        self.child[file.name] = file
        self.st.st_mtime = int(time())
        self.st.st_nlink += 1
    
    def remove_child(self, file: FsEntity):
        if file in self.child.keys():
            del self.child[file]
        else:
            raise FileNotFoundError(f"no child with name: '{file.name}'")
    
    def find_child(self, path: str):
        if path in self.child.keys():
            return self.child[path]
        else:
            raise FileNotFoundError(f"no child with path: '{path}'")
