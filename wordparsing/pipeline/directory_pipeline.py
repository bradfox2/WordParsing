'''continuous pipeline, processed per file.'''

#TODO: Idea: refactor into a class 'conversion pipeline' that can take a source, target, and a model.  source is a file directory or set of db ids and a connector, a target is a database, model is a model that is able to produce textual embeddings. 

import json
from hashlib import sha256
from pathlib import Path
from queue import Queue

import click
import numpy as np

from wordparsing.config import UNOCONV_SERVER_URL
from wordparsing.convert import Unoconv, convert
# Embed
##TODO: Clean up data structure for embedding object
from wordparsing.embed import embed_json_dumb
# Parse
### parse the docxs
from wordparsing.parse import parse_doc
from wordparsing.services.bert.bert import BertEmbService
from wordparsing.services.unoconv import start_unoconv
#start a unoconv serivce as docker container
from wordparsing.storage import engine
from wordparsing.storage.data_classes import (Embedding, Model, Session,
                                              TextPart)
from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list

# Convert
## Start a Unoconv Server for document conversion
if UNOCONV_SERVER_URL is None:
    UNOCONV_SERVER_URL,_ = start_unoconv('unoconv', 3000)
u = Unoconv(UNOCONV_SERVER_URL)

@click.command()
@click.option('--from_files_dir', default='./tests/docs', help='Directory of files to be converted.')
@click.option('--converted_files_dir', default='./converted', help='Directory to store converted files.')
@click.option('--convert_from_type', default='doc', help='Three letter extension of convert from type.')
@click.option('--convert_to_type', default='docx', help='Convert to this file type. Docx is supported right now.')
@click.option('--parsed_file_directory', default='./parsed', help='Temp storage directory for parsed files.')
@click.option('--commit', default=True, help='Commit these changes to database.')
def run_pipe(from_files_dir, converted_files_dir, convert_from_type, convert_to_type, parsed_file_directory, commit):        
    processing_queue = Queue()
    error_queue = Queue()

    for f in Path(from_files_dir).rglob('*.' + convert_from_type):
        processing_queue.put(f)

    #define embedding service
    bert = BertEmbService('BERT', 768, '0.1')
    
    m = Model(technique=bert.service_name,
              vec_length=bert.output_len,
              pooling_technique=bert.pooling_type,
              version_num=bert.version)

    while not processing_queue.empty():

        print(processing_queue.qsize())

        #open a alchemy session 
        sess = Session(engine)

        try:
            f = processing_queue.get()
            convert_path = convert(u, f, convert_from_type, convert_to_type, converted_files_dir)
            file_path = parse_doc(convert_path, parsed_file_directory)

            # dict where file path is key, (embedding, embedding style, embedding pooling technique) is value
            embedding = embed_json_dumb(file_path, bert)

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
                        #serialized_file=file_blob,
                        file_name=f.parts[-1],
                        json_str=json.dumps(raw_json),
                        file_hash=hash_of_file.hexdigest(),
                        hash_algo=hash_of_file.name)

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
