'''get it working, then do it right, then do it better'''
#running w finetuned model from cr classification training
#bert-serving-start -model_dir model/uncased_L-12_H-768_A-12/ -tuned_model_dir=model/classification_fine_tuning_test_1/ -ckpt_name="model.ckpt-343" -num_worker=1 -port 8190 -port_out 8191 -max_seq_len 100

from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list
#1.3s for 150 bert calls on 1080TI
#21s for 150 bert calls on i5-8600k

num_bert_calls = 0 

from bert_serving.client import BertClient
bc = BertClient(port=8190, port_out=8191)

import json
import numpy as np 

def convert_dict(d, txt):
    if type(d) is str:
        txt.append(d)
        return
    for k,v in d.items():
        txt.append(k)
        if type(v) is dict:
            convert_dict(v,txt)
        elif type(v) is list:
            for i in v:
                convert_dict(i,txt)
        else:
            txt.append(v)
    return txt

def embed_json_dumb(file_path):
    with open(file_path) as f:
        doc = json.load(f)

    d1 = heirarchical_dict_to_flat_list(doc,[])

    bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]

    d1_a = np.mean(np.array(bert_vectors), axis=0) 

    return d1_a, 'BERT', 'mean pooling'


if __name__ == '__main__':

    ### doc 1   
    with open('tests/converts/8218200.json') as f:
        doc = json.load(f)
    d1 = convert_dict(doc,[])       
    bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]
    d1_a = np.mean(np.array(bert_vectors), axis=0) 
    num_bert_calls+= len(bert_vectors)

    ### doc 2 
    with open('tests/converts/7787538.json') as f:
        doc = json.load(f)
    d2 = convert_dict(doc, [])       
    bert_vectors = [bc.encode([i]) for i in d2 if i.strip() not in  ['', None, 'None']]
    d2_a = np.mean(np.array(bert_vectors), axis=0)
    num_bert_calls+= len(bert_vectors)

    #sim
    cos_sim(d1_a[0],d2_a[0])

    ### doc 1   
    with open('tests/converts/8218200.json') as f:
        doc = json.load(f)
    d1 = convert_dict(doc,[])       
    bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]
    d1_a = np.mean(np.array(bert_vectors), axis=0)
    num_bert_calls+= len(bert_vectors)

    ### doc 2 
    with open('tests/docs/random_docs/recipe_1.json') as f:
        doc = json.load(f)
    d2 = convert_dict(doc, [])       
    bert_vectors = [bc.encode([i]) for i in d2 if i.strip() not in  ['', None, 'None']]
    d2_a = np.mean(np.array(bert_vectors), axis=0)
    num_bert_calls+= len(bert_vectors)

    #sim
    cos_sim(d1_a[0],d2_a[0])
