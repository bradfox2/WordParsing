import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine

load_dotenv(verbose=True, override=True)
TEXT_DB_PATH = os.getenv('TEXT_DB_PATH')
db_type = TEXT_DB_PATH.split(':')[0]
db_type_ok = {'oracle', 'sqlite'}

if db_type not in db_type_ok:
    raise NotImplementedError(f'Need dbtype in {db_type_ok}')

engine = create_engine(TEXT_DB_PATH, echo=True)
