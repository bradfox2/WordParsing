'''pipeline test'''

from wordparsing.fetch import (SWMS_MEDIA_FILER_PATH, SWMS_MEDIA_USER_NAME,
                               SWMS_MEDIA_USER_PASSWORD, Document, RemoteMount,
                               SWMSDocument, WorkInstruction)
from wordparsing.parse import parse_doc

rmtmnt = RemoteMount(SWMS_MEDIA_USER_NAME,
SWMS_MEDIA_USER_PASSWORD,
None,
SWMS_MEDIA_FILER_PATH)

rmtmnt.mounted_path

document = Document(rmtmnt.mounted_path + '9312122.DOCX')

doc = SWMSDocument.from_filer_file_name(rmtmnt, '9312122.DOCX')

document.file

parse_doc(doc.path,'./tests/converts/')

wi = WorkInstruction(None,None,None,None,document.file,None)

wi.from_file_path()
