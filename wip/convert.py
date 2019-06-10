'''Convert file via request to Unoconv.'''
import os
import platform
import re
from pathlib import Path, PurePath
import itertools

import click
import requests
import warnings

def build_conversion_url(conversion_url, file_type):
    return str(conversion_url + 'unoconv/' + file_type)

class Unoconv(object):
    
    """ Representation of a Unoconv server that will be used to convert documents.
    
    Arguments:
        url {str} -- Base URL of the Unoconv server.
    
    Properties:
        url {str} -- Base URL of Unoconv server, if it exists.
        formats {dict} -- Possible conversion formats.
        update {num} -- Current uptime.
    """
    
    def __init__(self, url):
        if requests.get(url).text is not None:
            self.url = url
            self.doc_types = requests.get(url + '/unoconv/formats').json()['document'] 
            self.extensions = {fmt['extension'] for fmt in self.doc_types}
            self.formats = {fmt['format'] for fmt in self.doc_types}
            self.fmt2ext = {f['format']:f['extension'] for f in self.doc_types}
        else:
            ValueError('Initial request to {} failed.'.format(url))
    
    @property
    def uptime(self):
        r = requests.get(self.url + '/healthz')
        return r.json()['uptime']
    
    @uptime.setter
    def uptime(self):
        warnings.warn('No setting uptime.')

    def build_conversion_url(self, file_format):
        """Constructs conversions URL based on format like /unoconv/{format-to-convert-to} per https://github.com/zrrrzzt/docker-unoconv-webservice
        
        Arguments:
            file_format {str} -- Converted file format type, not necessarily the extension.
        
        Returns:
            str -- URL that will convert to this file type.
        """
        return self.url + '/unoconv/' + self.fmt2ext[file_format]

def request_to_file(r, file_name, save_to_dir):
    """Save a request object contents to file.
    
    Arguments:
        r {Request} -- request object
        file_name {str} -- file name
        save_to_dir{Path} -- Path to save_to_dir
    """
    if not save_to_dir.exists():
        save_to_dir.mkdir()
    path = Path.cwd().joinpath(save_to_dir, file_name)
    with open(path, 'wb') as f:
            f.write(r.content)
    return True

def convert_file(unoconv, path, file_format, save_path):
    """Convert file at path to a new file type by using Unoconv object.
    
    Arguments:
        conversion_url {Unoconv} -- Unoconv object that points at Unoconv server used for file conversion.
        path {Path} -- Path of file that will be converted or directory of files
        file_format {str} -- File will be converted to this format.

    Returns:
        boolean - True if successful, None if not. 
    """

    if path.exists:
        print('Opening {}'.format(path))
        file = {'file': open(path, 'rb')}
    else:
        raise ValueError('{} does not exist.'.format(path))
    if file_format not in unoconv.formats:
        raise ValueError('Cannot convert to {} in this instance of Unoconv'.format(file_format))

    if type(save_path) is not Path:
        save_path = Path(save_path)
    
    url = unoconv.build_conversion_url(file_format)
    r = requests.post(url, files=file)

    if r:
        file_name = path.stem +'.' + unoconv.fmt2ext[file_format]
        return True if request_to_file(r, file_name, save_path) else None
    else:
        warnings.warn('Status Code {} from {}'.format(r.status_code, url))
        return None

def convert(unoconv, path, ext, file_format, save_path):
    """Convert file at path or files in directory at path to file format.
    
    Arguments:
        unoconv {Unoconv} -- Unoconv object
        path {str} -- Directory path where files reside.
        ext {str} -- Convert this extension.
        file_format {str} -- Convert to this format.
    """
    file_path = Path(path)
    save_dir = Path(save_path)
    save_dir.mkdir(exist_ok=True)
    
    if file_path.is_dir():
        files_0, files_1 = itertools.tee(file_path.glob('*'+'.'+ext)) #clone the generator so we can see the count of files
        len_files = sum(1 for _ in files_0) 
        print('{} files for conversion.'.format(len_files))
        for idx, file_ in enumerate(files_1):
            convert_file(unoconv, file_, file_format, save_path)
        return True
    else:
        convert_file(unoconv, file_path, file_format, save_path)
        return True
        
    return None

if __name__ == "__main__":
    u = Unoconv('http://s1:3000')
    #convert_file(u, 'docs/7787538.DOC', 'docx', 'converted')
    convert(unoconv=u, path='docs', ext='doc', file_format='docx', save_path='converted')

