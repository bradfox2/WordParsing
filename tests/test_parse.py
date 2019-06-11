'''test parsing'''

import inspect
import itertools
import json
import os
import pprint
from fractions import Fraction
from idlelib import paragraph
from pathlib import Path
from tkinter.ttk import Style
from zipfile import BadZipfile

import click
from docx import Document, styles

import pytest

from wordparsing.parse import parse_doc
from wordparsing.utils import count_files, rm_dir

test_dir = Path('tests')
doc_path = test_dir.joinpath('docxs')

@pytest.fixture(scope='function')
def save_path(keep_files):
    save_dir = test_dir.joinpath('converts')
    yield save_dir
    if not keep_files:
        rm_dir(save_dir)

def test_dir_parse(save_path):
    assert parse_doc(doc_path, save_path) == True
    assert count_files(save_path) == 2

    with open(save_path.joinpath('7787538.json')) as f:
        j = json.load(f)
    
    assert j is not None
    assert type(j) is dict
    assert len(j['Root']) == 74
    
def test_singlefile_parse(save_path):
    assert parse_doc(doc_path.joinpath('7787538.docx'), save_path) == True
    with open(save_path.joinpath('7787538.json')) as f:
        j = json.load(f)
    
    assert j is not None
    assert type(j) is dict
    assert len(j['Root']) == 74
    