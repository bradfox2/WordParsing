'''sqlalchemy data model classes defining embedding vectors [sqlite/oracle] database'''

import datetime
import io
import json
import os
import uuid
from hashlib import sha256

import numpy as np
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Sequence,
                        String, create_engine)
from sqlalchemy.dialects.sqlite import (
    BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, INTEGER, JSON,
    NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP, VARCHAR)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, backref, relationship, synonym

from wordparsing.storage import db_type, engine

Base = declarative_base()

def get_sqa_pk_col(db_type):
    '''Wrapper to create PKs from a sequence, add to this for different database types.
    '''
    return Column(Integer, Sequence('text_part_id'), primary_key=True)
    
class TextPart(Base):
    '''Table with records that describe chunks of text.
    '''
    __tablename__ = 'textpart'
    textpart_pk = get_sqa_pk_col(db_type)
    models = relationship('Embedding', back_populates='textpart')
    text_type = Column(TEXT)
    uuid = Column(TEXT, default = str(uuid.uuid4()))
    raw_text = Column(TEXT, index=True, unique=True)
    serialized_file = Column(BLOB)
    file_name = Column(TEXT)
    json_str = Column(TEXT)
    file_hash = Column(TEXT, index=True, unique=True)
    hash_algo = Column(TEXT)
    create_dttm = Column(DateTime, default=datetime.datetime.utcnow)

class Model(Base):
    '''Table with records that describe embedding models.
    '''
    __tablename__ = 'model'
    model_pk = get_sqa_pk_col(db_type)
    textparts = relationship('Embedding', back_populates='model')
    technique = Column(TEXT)
    create_dttm = Column(DATETIME, default=datetime.datetime.utcnow)
    vec_length = Column(INTEGER)
    pooling_technique = Column(TEXT)
    version_num = Column(TEXT)

class Embedding(Base):
    '''Many to many table relating text parts with embedding models, creating an embedding record. 
    '''
    __tablename__ = 'embedding'
    textpart_pk = Column(INTEGER, ForeignKey('textpart.textpart_pk'), primary_key=True)
    model_pk = Column(INTEGER, ForeignKey('model.model_pk'), primary_key=True)
    _vector = Column('vector', BLOB)

    @property
    def vector(self):
        '''deserialize np byte string from blob to obj'''
        return self._convert_array(self._vector)
    
    @vector.setter
    def vector(self, np_vec):
        '''serialize an np array obj into byte string for blob storage'''
        self._vector = self._adapt_array(np_vec)

    # allow getter and setter to exist on alchemy columns
    #https://gist.github.com/luhn/4170996
    vector = synonym('_vector', descriptor=vector)

    create_dttm = Column(DateTime, default=datetime.datetime.utcnow)
    textpart = relationship("TextPart", back_populates='models')
    model = relationship("Model", back_populates='textparts')

    def _convert_array(self, np_array):
        '''np array obj to np byte string'''
        out = io.BytesIO(np_array)
        out.seek(0)
        return np.load(out)

    def _adapt_array(self, np_array_byte_str):
        '''np byte string to a np array obj'''
        out = io.BytesIO()
        np.save(out, np_array_byte_str)
        out.seek(0)
        return out.read()

Base.metadata.create_all(engine)

if __name__ == "__main__":
    #insert one test record
    with open('./assets/test_doc.docx','rb') as f:
        blob = f.read()
    json_test = json.dumps({'a':['testing1', 'testing2']})
    hash_of_file = sha256(blob)
    
    t = TextPart(text_type="test text type",
                 raw_text="test raw text",
                 serialized_file=blob,
                 file_name='test file name',
                 json_str=json_test,
                 file_hash=hash_of_file.hexdigest(),
                 hash_algo=hash_of_file.name)

    m = Model(technique='test technique',
              vec_length=100,
              pooling_technique='test pooling',
              version_num='0.1.test')

    e = Embedding(vector=np.random.rand(10))

    sess = Session(engine)
    e.model = m
    t.models.append(e)
    sess.add(t)
    sess.commit()
