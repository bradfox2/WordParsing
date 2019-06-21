''' implement bert embedding service '''

#1.3s for 150 bert calls on 1080TI
#21s for 150 bert calls on i5-8600k

import atexit
import time

import numpy as np
from bert_serving.client import BertClient
from bert_serving.server import BertServer
from bert_serving.server.helper import get_args_parser

from wordparsing.config import (BERT_CPU_GPU, BERT_HTTP_PORT_IN,
                                BERT_HTTP_PORT_OUT, BERT_MODEL_DIR)
from wordparsing.embed import EmbeddingService

import subprocess

#TODO: bert service start-up via python command when run as a script appears to be broken for unknown reasons
#hacky loop to keep sleeping until we can connect to the service, but start service first time the module is loaded.
bc = BertClient(port=BERT_HTTP_PORT_IN, port_out=BERT_HTTP_PORT_OUT, timeout=1000, ignore_all_checks=True)
try:
    bc.server_status   
except TimeoutError as err:
    subprocess.Popen(f"bert-serving-start -model_dir {BERT_MODEL_DIR} -num_worker=1 -port {BERT_HTTP_PORT_IN} -port_out {BERT_HTTP_PORT_OUT} -max_seq_len 100")

while True:
    try: 
        bc.server_status
        err = None 
    except TimeoutError as err:
        pass
    
    if err:
        time.sleep(5)
    else:
        break

class BertEmbService(EmbeddingService):
    ''' embedding service using bert-as-a-service module'''

    def __init__(self, service_name, output_len, version):
        super().__init__(service_name, output_len, version)
        self.service_name = service_name
        self.output_len = output_len
        self.version = version
        self.pooling_type = 'avg'

    def encode_text(self, text):
        '''use bert-as-a-service to encode'''
        return bc.encode(text)

    def pool_vectors(self, vecs):
        '''dumb avg pooling'''
        d1_a = np.mean(np.array(vecs), axis=0) 
        return d1_a

if __name__ == '__main__':
    a = BertEmbService('BERT', 768, '1')    
    from wordparsing.embed import service_registry
    print(service_registry)