''' implement bert embedding service '''
#1.3s for 150 bert calls on 1080TI
#21s for 150 bert calls on i5-8600k

import numpy as np
from bert_serving.client import BertClient

from wordparsing.embed import EmbeddingService

#TODO: Factor out ports into args
bc = BertClient(port=8190, port_out=8191)

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
