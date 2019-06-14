"""Fetch documents from SWMS Media"""
import importlib
import inspect
import os
import warnings
from os.path import exists
from pathlib import Path, PureWindowsPath

import typed_ast
from docx import Document as docx_doc
from docx import styles
from dotenv import load_dotenv

from wordparsing.utils import count_files, count_files_fast

load_dotenv(verbose=True, override=True)
DEBUG = os.getenv('DEBUG')
SWMS_MEDIA_FILER_PATH = Path(os.getenv('SWMS_MEDIA_FILER_PATH'))
SWMS_MEDIA_USER_NAME = os.getenv('SWMS_MEDIA_USER_NAME')
SWMS_MEDIA_USER_PASSWORD = os.getenv('SWMS_MEDIA_USER_PASSWORD')

#files = os.scandir(SWMS_MEDIA_FILER_PATH)

class Document(object):
    def __init__(self, file):
        self.docx_obj = docx_doc(file)
        self.file = file

class RemoteMount(object):
    '''Mount a remote file system'''

    def __init__(self, user, password, mount_path, remote_path):
        self.mount_path = mount_path
        self.filer_path = remote_path
        self.user = user
        self.password = password
        self._mount_path = None if mount_path is  None else Path(mount_path)
        self._remote_path = None if remote_path is None else Path(remote_path)
        self._mounted_path = None
        self.mount_remote()
    
    @property
    def mounted_path(self):
        return self._mounted_path.as_posix()

    def mount_remote(self):
        if os.name == 'nt':
            if not self._remote_path.exists():
                print("Mounting")
                mount_command = self._prep_windows_mount_command(self.user, self.password, self._remote_path)
                self._mounted_path = self._remote_path
            else:
                warnings.warn("Remote already mounted.")
                self._mounted_path = self._remote_path
                return
        else:
            #untested
            mount_command = self._prep_linux_mount_command(self.user, self.password, self._mount_path, self._remote_path)
            self._mounted_path = self._mount_path.joinpath(self._remote_path) 
        
        os.system(mount_command)
        if self._mounted_path.exists():
            print("Connection success.")
        else:
            raise Exception("Failed to mount media directory.")
        return self._mounted_path
    
    def unmount_remote(self, mount_path):
        '''Unmount the remote filer'''
        raise NotImplementedError
    
    @property
    def not_allowed_strings(self):
        return ['$','&']

    def _sanitize_paths(self):
        if any(bs in self.filer_path for bs in self.not_allowed_strings):
            raise ValueError('Bad string in filer path.')

    def _check_filer_path_mounted(self):
        if self._mounted_path.exists():
            return True
        return False
    
    def _prep_linux_mount_command(self, user, password, mount_path, remote_path):
        #not tested
        return f'sudo mount -t cifs {mount_path} {remote_path} -o user={user},password={password},domain=nixcraft'

    def _prep_windows_mount_command(self, user, password, remote_path):
        return f"net use /user:{user} {remote_path} {password}"

class SWMSDocument(Document):

    @classmethod
    def all_from_wm_id(cls, wm_id, dbcon):
        """ Returns a list of SWMSDocument objects related to the provided WM_ID """
        #TODO: get media ids from swms
        media_ids = []
        return [cls.from_swms_media_id(x, dbcon) for x in media_ids]

    @classmethod
    def from_swms_media_id(cls, media_id, dbcon):
        #TODO: use dbcon to query SWMS, get path
        path = None
        return cls.from_file_path(path)

    @classmethod
    def from_file_path(cls, file_path):
        #TODO: fix this
        full_path = Path(file_path)
        return SWMSDocument(Document(full_path))

    @classmethod
    def from_filer_file_name(cls, remote_mount, file_name):
        '''remote mount and file name'''
        full_path = remote_mount.mounted_path + file_name
        return(SWMSDocument(Document(full_path)))

    def __init__(self, document):
        self.document = document
        self.path = document.file

class WorkInstruction(SWMSDocument):
    def __init__(self, wm_id, wt_id, rev, typ, file_path, SWMS_MEDIA_ID):
        #TODO: Refactor SWMSDocument into traditional factory pattern.
        super().__init__(Document(file_path))
        self.file_path = file_path 
        self.wm_id = wm_id
        self.wt_it = wt_id
        self.rev = rev
        self.typ = typ
        self.steps = []     

if __name__ == '__main__':
    pass
