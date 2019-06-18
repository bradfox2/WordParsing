''' common utils and classes for sql alchemy'''

#https://docs.sqlalchemy.org/en/13/core/custom_types.html

#//TODO: This doesnt seem to work, returns all Nones.

#class to implement a UUID custom type. 
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

class GUID(TypeDecorator):
    """UUID type
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        print(dialect)
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):

        if value is None:
            print(value)
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value