'''continuous pipeline, processed per file.'''

#TODO: Idea: refactor into a class 'conversion pipeline' that can take a source, target, and a model.  source is a file directory or set of db ids and a connector, a target is a database, model is a model that is able to produce textual embeddings. 

import json
from hashlib import sha256
from pathlib import Path
from queue import Queue

import click
import numpy as np
from bert_serving.client import BertClient

from wordparsing.convert import Unoconv, convert
# Embed
##TODO: Clean up data structure for embedding object
from wordparsing.embed import embed_json_dumb
# Parse
### parse the docxs
from wordparsing.parse import parse_doc
from wordparsing.storage import engine
from wordparsing.storage.data_classes import (Embedding, Model, Session,
                                              TextPart)
from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list

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

## set parsed file dir 
parse_file_dir = './tests/pipeline/parsed'

@click.command()
@click.option('--commit', help='Commit these changes to database.')
def run_pipe(commit):        
    processing_queue = Queue()
    error_queue = Queue()

    for f in files_dir.rglob('*.'+convert_from):
        processing_queue.put(f)

    while not processing_queue.empty():

        print(processing_queue.qsize())

        #open a alchemy session 
        sess = Session(engine)

        try:
            f = processing_queue.get()
            convert_path = convert(u, f, convert_from, convert_to, converted_dir)
            file_path = parse_doc(convert_path, parse_file_dir)

            # dict where file path is key, (embedding, embedding style, embedding pooling technique) is value
            embedding, model_type, pooling_type = embed_json_dumb(file_path)

            # Store
            #TODO: Refactor arguments here to be constructed from other classes, maybe a factory that can produce the data classes based on input files.

            #TODO: May need to consider having common object(s) that moves through the pipeline, or will have to pass all the intial file information along.

            with open(Path(f),'rb') as fle:
                file_blob = fle.read()

            with open(file_path) as jsn:
                raw_json = json.load(jsn)
            
            raw_text = heirarchical_dict_to_flat_list(raw_json, [])

            hash_of_file = sha256(file_blob)

            t = TextPart(text_type="Test Pipeline Document, Work Instruction",
                        raw_text='\n'.join(raw_text),
                        serialized_file=file_blob,
                        file_name=f.parts[-1],
                        json_str=json.dumps(raw_json),
                        file_hash=hash_of_file.hexdigest(),
                        hash_algo=hash_of_file.name)

            m = Model(technique=model_type,
                    vec_length=len(embedding[0]),
                    pooling_technique=pooling_type,
                    version_num='test')

            e = Embedding(vector=embedding[0])

            new_t = sess.query(TextPart).filter(TextPart.file_hash == t.file_hash).first()
            if new_t:
                t = new_t

            e.model = m 
            t.models.append(e)
            
            print(t.uuid)

            sess.add(t)

            if commit:
                sess.commit()

        except Exception as e:
            print(f"{f} failed conversion.")
            print(e)
            sess.rollback()
            error_queue.put(f)
        
        finally:
            sess.close()
        
if __name__ == "__main__":
    run_pipe()
