from __future__ import annotations
import stat, errno
from fuse import FUSE, Operations, LoggingMixIn, FuseOSError
from collections import defaultdict

from time import time

from PyQt5 import QtCore




class Memory(LoggingMixIn, Operations, QtCore.QObject):
    'Example memory filesystem. Supports only one level of files.'
    s_log = QtCore.pyqtSignal(str)
    s_warning = QtCore.pyqtSignal(str)

    def __init__(self):
        super(QtCore.QObject, self).__init__()
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(
            st_mode=(stat.S_IFDIR | 0o755),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2)

    def wrapped(func):
        def called(self: Memory, *args, **kwargs):
            result = func(self, *args, **kwargs)
            msg = f"{func.__name__}, {args}, {kwargs} -> {result}"
            print(msg)
            self.s_log.emit(msg)

            return result
        return called

    @wrapped
    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    @wrapped
    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    @wrapped
    def create(self, path, mode):
        self.files[path] = dict(
            st_mode=(stat.S_IFREG | mode),
            st_nlink=1,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        self.fd += 1
        return self.fd

    @wrapped
    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)

        return self.files[path]

    @wrapped
    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ""       # Should return ENOATTR
            # return FuseOSError(errno.ENOENT)

    @wrapped
    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    @wrapped
    def mkdir(self, path, mode):
        self.files[path] = dict(
            st_mode=(stat.S_IFDIR | mode),
            st_nlink=2,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        self.files['/']['st_nlink'] += 1

    @wrapped
    def open(self, path, flags):
        self.fd += 1
        return self.fd

    @wrapped
    def read(self, path, size, offset, fh):
        return self.data[path][offset:offset + size]

    @wrapped
    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    @wrapped
    def readlink(self, path):
        return self.data[path]

    @wrapped
    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    @wrapped
    def rename(self, old, new):
        self.data[new] = self.data.pop(old)
        self.files[new] = self.files.pop(old)

    @wrapped
    def rmdir(self, path):
        # with multiple level support, need to raise ENOTEMPTY if contains any files
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    @wrapped
    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    @wrapped
    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    @wrapped
    def symlink(self, target, source):
        self.files[target] = dict(
            st_mode=(stat.S_IFLNK | 0o777),
            st_nlink=1,
            st_size=len(source))

        self.data[target] = source

    @wrapped
    def truncate(self, path, length, fh=None):
        # make sure extending the file fills in zero bytes
        self.data[path] = self.data[path][:length].ljust(
            length, '\x00'.encode('ascii'))
        self.files[path]['st_size'] = length

    @wrapped
    def unlink(self, path):
        self.data.pop(path)
        self.files.pop(path)

    @wrapped
    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    @wrapped
    def write(self, path, data, offset, fh):
        self.data[path] = (
            # make sure the data gets inserted at the right offset
            self.data[path][:offset].ljust(offset, '\x00'.encode('ascii'))
            + data
            # and only overwrites the bytes that data is replacing
            + self.data[path][offset + len(data):])
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)
