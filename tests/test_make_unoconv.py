import pytest
import requests

def test_unoconv(make_unoconv_container):
    uno_server_url,_ = make_unoconv_container
    assert requests.get(uno_server_url+'/healthz').ok
