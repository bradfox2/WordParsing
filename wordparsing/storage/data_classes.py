'''sqlalchemy data model classes defining embedding vector [sqlite/oracle] database'''

import uuid
import datetime
from sqlalchemy import Column, Integer, String, \
    create_engine, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, Session
from sqlalchemy.ext.declarative import declarative_base
from wordparsing.storage import db_type, engine
from sqlalchemy.dialects.sqlite import \
            BLOB, BOOLEAN, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
            INTEGER, NUMERIC, JSON, SMALLINT, TEXT, TIME, TIMESTAMP, \
            VARCHAR

Base = declarative_base()

def get_sqa_pk_col(db_type):
    if db_type.lower() == 'oracle':
        return Column(Integer, Sequence('text_part_id'), primary_key=True)

    elif db_type.lower() == 'sqlite':
         return Column(Integer, primary_key=True)
    else:
        raise ValueError('id column cannot be initiated.')
    
class TextPart(Base):
    __tablename__ = 'textpart'
    textpart_pk = get_sqa_pk_col(db_type)
    models = relationship("Model", secondary='embeddings')
    text_type = Column(TEXT)
    uuid = Column(TEXT, default = str(uuid.uuid4()))
    raw_text = Column(TEXT)
    serialized_file = Column(BLOB)
    file_name = Column(TEXT)
    json_str = Column(TEXT)
    file_hash = Column(TEXT)
    hash_algo = Column(TEXT)
    create_dttm = Column(DateTime, default=datetime.datetime.utcnow)

class Model(Base):
    __tablename__ = 'model'
    model_pk = get_sqa_pk_col(db_type)
    textpart_fk = relationship('TextPart', secondary = 'embeddings')
    technique = Column(TEXT)
    create_dttm = Column(DATETIME, default=datetime.datetime.utcnow)
    vec_length = Column(NUMERIC)
    pooling_technique = Column(TEXT)
    version_num = Column(NUMERIC)

class Embeddings(Base):
    __tablename__ = 'embeddings'
    embeddings_pk = get_sqa_pk_col(db_type)
    textpart_pk = Column(INTEGER, ForeignKey('textpart.textpart_pk'))
    model_pk = Column(INTEGER, ForeignKey('model.model_pk'))
    vector = Column(BLOB)
    create_dttm = Column(DateTime, default=datetime.datetime.utcnow)

    textpart = relationship(TextPart, backref=backref("embeddings", cascade='all, delete-orphan'))
    model = relationship(Model, backref=backref("model", cascade='all, delete-orphan'))
    
Base.metadata.create_all(engine)

if __name__ == "__main__":
    m = Model()
    t = TextPart()
    e = Embeddings()
