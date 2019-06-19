
#automap nims database
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData

m = MetaData(schema='NIMS')

Base = automap_base(bind = engine, metadata=m)

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine('', echo='debug')

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.

session = Session(engine)

session.query(Base.classes.media_details).first()

# rudimentary relationships are produced
session.add(Address(email_address="foo@bar.com", user=User(name="foo")))
session.commit()

# collection-based relationships are by default named
# "<classname>_collection"
print (u1.address_collection)

Base.classes.keys()

session.query(Base.classes.s_work_tasks).first()

from sqlalchemy.inspection import inspect 
inspect(Base.classes.l_work_mechanisms).relationships.items()

Base.classes.s_work_tasks.__table__