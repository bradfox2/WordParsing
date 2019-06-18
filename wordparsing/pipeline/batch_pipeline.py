''' batch conversion pipeline,  process all documents per step.  Doesnt seem to be a good idea.'''

#TODO: Idea: refactor into a class 'conversion pipeline' that can take a source, target, and a model.  source is a file directory or set of db ids and a connector, a target is a database, model is a model that is able to produce textual embeddings. 

import json
from hashlib import sha256
from pathlib import Path, rglob

import numpy as np
from bert_serving.client import BertClient

from wordparsing.storage import engine
from wordparsing.convert import Unoconv, convert
from wordparsing.storage.data_classes import (Embedding, Model, Session,
                                              TextPart)
from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list

from pathlib import Path

## Start a BERT Client for vectorization
bc = BertClient(port=8190, port_out=8191)

# Convert
## Start a Unoconv Server for document conversion
u = Unoconv('http://s1:3000')

### specify conversion path
files_dir = Path('./tests/docs')
### specify save directory 
converted_dir = './tests/pipeline/converted'
### specify conversion from and to
convert_from = 'doc'
convert_to = 'docx'
### perform conversion

#for file in files_dir.rglob('*.'+convert_from):
#    print(file)

convert(u, files_dir, convert_from, convert_to, converted_dir)

# Parse
### parse the docxs
from wordparsing.parse import parse_doc
## set parsed file dir 
parse_file_dir = './tests/pipeline/parsed'
file_list = list(Path(parse_file_dir).rglob('*.docx'))
for path in file_list:
    parse_doc(converted_dir, parse_file_dir)

# Embed
##TODO: Clean up data structure for embedding object
from wordparsing.embed import embed_json_dumb
# dict where file path is key, (embedding, embedding style, embedding pooling technique) is value
embed_d = {str(path.absolute().as_posix()): embed_json_dumb(path) for path in list(Path(parse_file_dir).rglob('*.json'))}

# Store
#TODO: Refactor arguments here to be constructed from other classes, maybe a factory that can produce the data classes based on input files.

#TODO: May need to consider having common object(s) that moves through the pipeline, or will have to pass all the intial file information along.

for path, emb in embed_d.items():

    with open(Path(path),'rb') as f:
        blob = f.read()

    hash_of_file = sha256(blob)

    t = TextPart(text_type="Test Pipeline Document Hard Code",
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
