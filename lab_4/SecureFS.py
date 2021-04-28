from os import getxattr
import os
from fuse import Operations, LoggingMixIn, FuseOSError, fuse_context, fuse_get_context
import stat, errno
from PyQt5 import QtCore

from lab_4.other import logging
from lab_4.FdGenerator import FdGenerator
from lab_4.Fs import Level, Stat, User, FsEntity, File, Dir



# class SecureFS(LoggingMixIn, Operations, QtCore.QObject):
class SecureFS(Operations, QtCore.QObject):
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.root: FsEntity = Dir(name="/", user=User())
        self.root.add_child(File('test', b'123', User()))
        self.mkdir('/secure', stat.S_IFDIR | 0o644)
        for level in [Level.NonSecret, Level.Secret, Level.TopSecret]:
            self.root.add_child(Dir(level.to_str(), User()))

    def create(self, path: str, mode: int, fi=0) -> int:
        basename = "/".join(path.split('/')[:-1])
        filename = path.split('/')[-1]
        if mode & stat.S_IFDIR:
            self.get_dir(basename).add_child(Dir(filename, User()))
        else:
            self.get_dir(basename).add_child(File(filename, b'', User()))
        return FdGenerator.new_file(path)

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
            return self.get_entity(path).st.dict()
        except:
            logging.debug(f'not found: {path}')
            print(self.root.json())
            raise FuseOSError(errno.ENOENT)
    
    # def getxattr(self, path, name, position=0):
    #     # return self.getattr(path)
    #     return {}

    getxattr = None

    # def open(self, path, flags):
    #     # return super().open(path, flags)
    #     return FdGenerator.new_fd()
    
    def readdir(self, path, fh):
        logging.debug(f"reading dir on '{path}'")
        return ['.', '..'] + list(self.get_dir(path).child.keys())

    def read(self, path: str, size: int, offset: int, fh):
        logging.debug(f"uid: {fuse_get_context()}")
        return self.get_file(path).data[offset:offset+size]
    
    def write(self, path: str, data: bytes, offset: int, fh):
        try:
            file: File = self.get_file(path)
            file.data = file.data[:offset].encode() + data + file.data[offset+len(data):].encode()
            file.st.st_size = len(file.data)
            return len(data)
        except:
            raise FuseOSError(errno.ENOENT)

    def truncate(self, path: str, length: int, fh=0):
        file: File = self.get_file(path)
        file.data = '\x00'*length
        file.st.st_size = len(file.data)
        
    def mkdir(self, path, mode):
        basename = "/".join(path.split('/')[:-1])
        filename = path.split('/')[-1]
        self.get_dir(basename).add_child(Dir(filename, User()))
        return FdGenerator.new_file(path)
        
        
    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
    
    def rmdir(self, path):
        # self.get_dir(path)
        logging.debug(path)

    def unlink(self, path):
        logging.debug(path)
    
    def releasedir(self, path, fh):
        logging.debug(path)
        
        