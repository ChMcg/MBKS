from __future__ import annotations
import os
import json
from fuse import Operations, LoggingMixIn, FuseOSError, fuse_context, fuse_get_context
import stat, errno
from PyQt5 import QtCore

from lab_4.other import logging
from lab_4.FdGenerator import FdGenerator
from lab_4.Fs import Level, Stat, User, FsEntity, File, Dir


class SecureFS(Operations, QtCore.QObject):
    s_log = QtCore.pyqtSignal(str)
    s_warning = QtCore.pyqtSignal(str)
    users_updated = QtCore.pyqtSignal()

    def wrapped(func):
        def called(self: SecureFS, *args, **kwargs):
            result = func(self, *args, **kwargs)
            msg = f"{func.__name__}, {args}, {kwargs} -> {result}"
            self.s_log.emit(msg)
            print(msg)
            return result
        return called

    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.users: dict[int, User] = {}
    
    def scan_users(self):
        with open("/etc/passwd", 'r') as f:
            for line in f.readlines():
                name, x, uid, gid, _, _, _ = line.strip().split(':')
                uid = int(uid)
                gid = int(gid)
                if uid >= 1000:
                    self.s_log.emit(f"[passwd]: {name, uid, gid}")
                    user = User(name, uid, gid)
                    self.users[uid] = user
                    self.s_log.emit(user.json())
        self.users_updated.emit()
    
    def set_user_level(self, uid: int, level: Level):
        user = self.users[uid]
        self.s_log.emit(f"Changing user access level: [{user.login}]: {user.access_level.to_str()} -> {level.to_str()}")
        self.users[uid].access_level = level
        print('user level:', (uid, level))
    
    def create_default_dirs(self):
        user = self.users[1000]
        self.root: FsEntity = Dir(name="/", user=user)
        for level in [Level.NonSecret, Level.Secret, Level.TopSecret]:
            self.root.add_child(Dir(level.to_str(), user, level=level))

    def get_current_user(self) -> User:
        uid, gid, pid = fuse_get_context()
        if uid not in self.users:
            self.s_warning.emit(f"Unknown user: {uid, gid}")
            raise KeyError("User not found")
        else:
            print('user found:', self.users[uid].json())
            return self.users[uid]

    @wrapped
    def create(self, path: str, mode: int, fi=0) -> int:
        basename = "/".join(path.split('/')[:-1])
        user = self.get_current_user()
        filename = path.split('/')[-1]
        dir = self.get_dir(basename)
        if user.access_level < dir.level:
            self.s_warning.emit(f"Заблокирована попытка создания файла: {user.login} -> {filename} в директории {basename}")
            return -1;
        if mode & stat.S_IFDIR:
            dir.add_child(Dir(filename, user, level=dir.level))
        else:
            dir.add_child(File(filename, b'', user, level=dir.level))
        return 0

    def get_entity(self, path: str) -> FsEntity:
        tmp: Dir = self.root
        path_names = path.split('/')
        while '' in path_names:
            path_names.remove('')
        for ent in path_names:
            if tmp.is_dir() and ent in tmp.child.keys():
                tmp = tmp.child[ent]
            else:
                raise FuseOSError(errno.ENOENT)
        return tmp
    
    def get_dir(self, path: str) -> Dir:
        return self.get_entity(path)
    
    def get_file(self, path: str) -> File:
        return self.get_entity(path)
    
    def getattr(self, path: str, fh = None) -> Stat:
        try:
            logging.debug(f"getxattr for: {path}")
            return self.get_entity(path).st.dict()
        except:
            logging.debug(f'not found: {path}')
            raise FuseOSError(errno.ENOENT)
    
    getxattr = None

    def readdir(self, path, fh):
        logging.debug(f"reading dir on '{path}'")
        user = self.get_current_user()
        dir = self.get_dir(path)
        if dir.level <= user.access_level:
            return ['.', '..'] + list(self.get_dir(path).child.keys())
        else:
            return ['.', '..']

    @wrapped
    def read(self, path: str, size: int, offset: int, fh):
        logging.debug(f"uid: {fuse_get_context()}")
        self.s_log.emit(f"reading: {path} ({fh})")
        file = self.get_file(path)
        user = self.get_current_user()
        if user.access_level < file.level:
            self.s_warning.emit(f"Заблокирована попытка чтения: {user.login} -> {file.name}")
            raise FuseOSError(errno.EACCES)
        else:
            return self.get_file(path).data[offset:offset+size]
    
    @wrapped
    def write(self, path: str, data: bytes, offset: int, fh):
        try:
            user = self.get_current_user()
            file: File = self.get_file(path)
            if user.access_level > file.level:
                self.s_warning.emit(f"Заблокирована попытка записи: {user.login} -> {file.name}")
                raise FuseOSError(errno.EACCES)
            if isinstance(data, str):
                data = data.encode()
            print('concatenating:', (file.data[:offset], data, file.data[offset+len(data):]))
            if len(file.data) == 0:
                file.data = data
            else:
                file.data = file.data[:offset] + data + file.data[offset+len(data):]
            file.st.st_size = len(file.data)
            return len(data)
        except:
            raise FuseOSError(errno.ENOENT)

    @wrapped
    def truncate(self, path: str, length: int, fh=0):
        file: File = self.get_file(path)
        file.data = '\x00'*length
        file.st.st_size = len(file.data)
        return 0
        
    @wrapped
    def mkdir(self, path, mode):
        basename = "/".join(path.split('/')[:-1])
        filename = path.split('/')[-1]
        self.get_dir(basename).add_child(Dir(filename, User('admin')))
        return 0
        
    @wrapped
    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
    
    @wrapped
    def rmdir(self, path: str):
        self.s_log.emit(f"rmdir: {path}")
        logging.debug(path)
        basename = "/".join(path.split('/')[:-1])
        target_dir_name = path.split('/')[-1]
        dir: Dir = self.get_dir(basename)
        for childname, child in dir.child.items():
            logging.debug(childname)
            self.s_log.emit(childname)
            if childname == target_dir_name:
                self.s_log.emit(f"Removing: {child}")
                dir.remove_child(child)
                break

    @wrapped
    def unlink(self, path):
        logging.debug(path)
        logging.debug(path)
        basename = "/".join(path.split('/')[:-1])
        target_dir_name = path.split('/')[-1]
        dir: Dir = self.get_dir(basename)
        for childname, child in dir.child.items():
            logging.debug(childname)
            self.s_log.emit(childname)
            if childname == target_dir_name:
                self.s_log.emit(f"Removing: {child}")
                dir.remove_child(child)
                break
    
    def releasedir(self, path, fh):
        logging.debug(path)
        
        