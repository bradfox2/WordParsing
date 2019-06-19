'''continuous pipeline, processed per file.'''

#TODO: Idea: refactor into a class 'conversion pipeline' that can take a source, target, and a model.  source is a file directory or set of db ids and a connector, a target is a database, model is a model that is able to produce textual embeddings. 

import json
import os
# Docs from media id
#swms_docs = SWMSDocument.all_from_wm_id(5144071, wordparsing.fetch.engine, smws_filer_mount)
# Docs from raw Query
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from queue import Queue

import click
import numpy as np
from bert_serving.client import BertClient
from dotenv import load_dotenv

import wordparsing.fetch
import wordparsing.storage
from wordparsing.convert import Unoconv, convert
# Embed
##TODO: Clean up data structure for embedding object
from wordparsing.embed import embed_json_dumb
from wordparsing.fetch import RemoteMount, SWMSDocument
# Parse
### parse the docxs
from wordparsing.parse import parse_doc
#start a unoconv serivce as docker container
from wordparsing.services.unoconv import UNOCONV_URL
from wordparsing.storage.data_classes import (Embedding, Model, Session,
                                              TextPart)
from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list

load_dotenv(verbose=True, override=True)

## Start a BERT Client for vectorization
bc = BertClient(port=8190, port_out=8191)

# Convert
## Start a Unoconv Server for document conversion
u = Unoconv(UNOCONV_URL)

### specify conversion path
#files_dir = Path('./tests/docs')
DEBUG = os.getenv('DEBUG')
SWMS_MEDIA_FILER_PATH = Path(os.getenv('SWMS_MEDIA_FILER_PATH'))
SWMS_MEDIA_USER_NAME = os.getenv('SWMS_MEDIA_USER_NAME')
SWMS_MEDIA_USER_PASSWORD = os.getenv('SWMS_MEDIA_USER_PASSWORD')

smws_filer_mount = RemoteMount(SWMS_MEDIA_USER_NAME,
                                SWMS_MEDIA_USER_PASSWORD,
                                None,
                                SWMS_MEDIA_FILER_PATH)

#load NIMS connection information
NIMS_CONNECTION_STRING = os.getenv('NIMS_CONNECTION_STRING')
NIMSsession = Session(wordparsing.fetch.engine)

yesterday = date.today() - timedelta(days=1)
swms_docs = SWMSDocument.all_from_raw_query('queries/media_details_from_date.sql',
                                             {"yesterday": yesterday}, 
                                             wordparsing.fetch.engine,
                                              smws_filer_mount)

### specify save directory 
converted_dir = './converted'

### specify conversion from and to
convert_from = 'doc'
convert_to = 'docx'

## set parsed file dir 
parse_file_dir = './parsed'

#TODO: This will need to be multithreaded to be fast enough.  Currently about 3s per record.

@click.command()
@click.option('--commit', help='Commit these changes to database.')
def run_pipe(commit):        
    processing_queue = Queue()
    error_queue = Queue()

    for f in swms_docs:
        processing_queue.put(f)

    while not processing_queue.empty():

        print(processing_queue.qsize())

        #open a alchemy session 
        sess = Session(wordparsing.storage.engine)

        try:
            f = processing_queue.get()
            convert_path = convert(u, f.path, convert_from, convert_to, converted_dir)
            file_path = parse_doc(convert_path, parse_file_dir)

            # dict where file path is key, (embedding, embedding style, embedding pooling technique) is value
            embedding, model_type, pooling_type = embed_json_dumb(file_path)

            # Store
            #TODO: Refactor arguments here to be constructed from other classes, maybe a factory that can produce the data classes based on input files.

            #TODO: May need to consider having common object(s) that moves through the pipeline, or will have to pass all the intial file information along.

            #TODO: Keep these files in memory, somehow.

            with open(Path(f.path),'rb') as fle:
                file_blob = fle.read()

            with open(file_path) as jsn:
                raw_json = json.load(jsn)
            
            raw_text = heirarchical_dict_to_flat_list(raw_json, [])

            hash_of_file = sha256(file_blob)

            t = TextPart(text_type="Test Pipeline Document, Work Instruction",
                        raw_text='\n'.join(raw_text),
                        serialized_file=file_blob,
                        file_name=Path(f.path).parts[-1],
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
            
            sess.add(t)

            if commit:
                sess.commit()

        except Exception as e:
            #TODO: Persist these convrsion errors, maybe add them to another db table?
            print(f"{f.path} failed conversion.")
            print(e)
            sess.rollback()
            error_queue.put(f)
        
        finally:
            sess.close()
        
if __name__ == "__main__":
    run_pipe()
