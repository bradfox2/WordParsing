import requests
from wip.convert import request_to_file, convert, Unoconv
from pathlib import Path
import pytest
import os

test_dir = Path('tests')
test_request_saves = test_dir.joinpath('request_saves')
test_converted_docs = test_dir.joinpath('converted')

@pytest.fixture(scope="module")
def setup_request():
    yield requests.get('http://google.com')
    #teardown code here
    Path.unlink(test_request_saves.joinpath('google.html'))
    Path.rmdir(test_request_saves)
    
def test_request_to_file(setup_request):
    request_to_file(setup_request, 'google.html', test_request_saves)
    assert test_request_saves.exists()
    assert test_request_saves.is_dir()
    assert test_request_saves.joinpath('google.html').exists()

@pytest.fixture
def no_rsrc(request):
    #nothing before test
    yield
    #return an always run function post test
    def rm_conv_files():
        '''tear down function to remove converted files'''
        for file in test_converted_docs.glob('*'):
            Path.unlink(file)
        Path.rmdir(test_converted_docs)
    request.addfinalizer(rm_conv_files)
    return no_rsrc

def test_convert(uno_server_url, no_rsrc):
    """ Ensure 'convert' converts everything in ./tests/docs/.

    uno_server_url is a command line argument, see conftest.py
    
    no_rsrc is a placeholder fixture so that the converted files are always torn down, no resources are generated from this fixture.
    """
    u = Unoconv(uno_server_url)    
    assert convert(unoconv=u, path='tests/docs', ext='doc', file_format='docx', save_path='tests/converted') is True
    assert test_converted_docs.exists()
    assert test_converted_docs.is_dir()
    assert len(list(test_converted_docs.glob('*.docx'))) == 2
