import pytest
from pathlib import Path
from wordparsing.services.unoconv import start_unoconv
import uuid

def pytest_addoption(parser):
    """ Add cmd line options to pytest
    """
    parser.addoption("--keep_files", action='store', default=True, help='Keep the directories and files created by testing.')

@pytest.fixture
def keep_files(request):
    """Boolean cmd line option to keep files from testing around.
    """
    return request.config.getoption("--keep_files")

@pytest.fixture(scope='session')
def make_unoconv_container():
    ''' start and yield an unoconv test docker container'''
    unourl, unoobj = start_unoconv('uno_test', 3001)
    yield unourl, unoobj
    #unoobj.stop()