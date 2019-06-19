'''get it working, then do it right, then do it better'''
#running w finetuned model from cr classification training
#bert-serving-start -model_dir model/uncased_L-12_H-768_A-12/ -tuned_model_dir=model/classification_fine_tuning_test_1/ -ckpt_name="model.ckpt-343" -num_worker=1 -port 8190 -port_out 8191 -max_seq_len 100

import json

import numpy as np

from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list #pylint: disable=import-error,no-name-in-module

service_registry = []
def register_service(target_class):
        service_registry.append(target_class)

class EmbeddingServiceRegistry(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_service(cls)
        return cls
class EmbeddingService(object, metaclass = EmbeddingServiceRegistry):
    def __init__(self, service_name, output_len, version):
        self.service_name = service_name
        self.output_len = output_len
        self.version = version
    
    def encode_text(self, text):
        """Take a list of text chunks and return a self.output_len vector/1-d array
        
        Arguments:
            text {str} -- chunks to encode
        
        Raises:
            NotImplementedError: 
        """
        raise NotImplementedError
    
    def pool_vectors(self, vector_array):
        """Take a 2d array of n number of self.output_length length vectors and return a 1-d array/1-d vector of self.output_len.
        
        Arguments:
            vector_array {numpy.array} -- 2-d numpy array representing related chunks of text

        Raises:
            NotImplementedError
        """
        raise NotImplementedError
    
    #TODO: Create a service registry.   


def embed_json_dumb(file_path, embedding_service):
    """simple 'element by element' embedding of text formatted in json
    
    Arguments:
        file_path {str or Path} -- path to json file
        embedding_service {EmbeddingService} -- Embedding service providing 'encode_text' and 'pool_vectors' methods.
    
    Returns:
        Numpy Array -- numpy array of the json file 
    """
    pool_vectors = embedding_service.pool_vectors
    encode_text = embedding_service.encode_text

    with open(file_path) as f:
        doc = json.load(f)

    d1 = heirarchical_dict_to_flat_list(doc,[])

    #bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]
    bert_vectors = [encode_text([i]) for i in d1 if i.strip() not in  ['', None, 'None']]

    #d1_a = np.mean(np.array(bert_vectors), axis=0) 
    d1_a = pool_vectors(bert_vectors)
    return d1_a

if __name__ == '__main__':
    pass
    # ### doc 1   
    # with open('tests/converts/8218200.json') as f:
    #     doc = json.load(f)
    # d1 = heirarchical_dict_to_flat_list(doc,[])       
    # bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]
    # d1_a = np.mean(np.array(bert_vectors), axis=0) 

    # ### doc 2 
    # with open('tests/converts/7787538.json') as f:
    #     doc = json.load(f)
    # d2 = heirarchical_dict_to_flat_list(doc, [])       
    # bert_vectors = [bc.encode([i]) for i in d2 if i.strip() not in  ['', None, 'None']]
    # d2_a = np.mean(np.array(bert_vectors), axis=0)

    # #sim
    # cos_sim(d1_a[0],d2_a[0])

    # ### doc 1   
    # with open('tests/converts/8218200.json') as f:
    #     doc = json.load(f)
    # d1 = heirarchical_dict_to_flat_list(doc,[])       
    # bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]
    # d1_a = np.mean(np.array(bert_vectors), axis=0)

    # ### doc 2 
    # with open('tests/docs/random_docs/recipe_1.json') as f:
    #     doc = json.load(f)
    # d2 = heirarchical_dict_to_flat_list(doc, [])       
    # bert_vectors = [bc.encode([i]) for i in d2 if i.strip() not in  ['', None, 'None']]
    # d2_a = np.mean(np.array(bert_vectors), axis=0)

    # #sim
    # cos_sim(d1_a[0],d2_a[0])
