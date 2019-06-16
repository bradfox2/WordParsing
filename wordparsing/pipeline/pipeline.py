'''test conversion pipeline'''

import json
from hashlib import sha256
from pathlib import Path

import numpy as np
from bert_serving.client import BertClient

from wordparsing.storage import engine
from wordparsing.storage.data_classes import (Embedding, Model, Session,
                                              TextPart)
from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list

bc = BertClient(port=8190, port_out=8191)


path_to_file = Path('./tests/converts/8218200.json')

with open(path_to_file) as f:
    doc = json.load(f)

d1 = heirarchical_dict_to_flat_list(doc,[])

bert_vectors = [bc.encode([i]) for i in d1 if i.strip() not in  ['', None, 'None']]

d1_a = np.mean(np.array(bert_vectors), axis=0) 


#TODO: Refactor arguments here to be constructed from other classes, maybe a factory that can produce the data classes based on input files.

with open('tests/converts/8218200.json','rb') as f:
    blob = f.read()

hash_of_file = sha256(blob)


t = TextPart(text_type="WorkInstruction",
             raw_text='\n'.join(d1),
             serialized_file=blob,
             file_name=path_to_file.parts[-1],
             json_str=json.dumps(doc),
             file_hash=hash_of_file.hexdigest(),
             hash_algo=hash_of_file.name)

m = Model(technique='BERT',
          vec_length=len(d1_a),
          pooling_technique='mean',
          version_num='0.1.initial')

e = Embedding(vector=d1_a)

sess = Session(engine)

new_t = sess.query(TextPart).filter(TextPart.file_hash == t.file_hash).first()
if new_t:
    t = new_t

e.model = m 
t.models.append(e)

sess.add(t)
sess.commit()

#sess.rollback()
#Session.close_all()
