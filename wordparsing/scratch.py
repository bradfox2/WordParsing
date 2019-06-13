import wordparsing.fetch
from wordparsing.fetch import (SWMS_MEDIA_FILER_PATH, SWMS_MEDIA_USER_NAME,
                               SWMS_MEDIA_USER_PASSWORD, RemoteMount,
                               SWMSDocument)

from wordparsing.convert import 

rmtmnt = RemoteMount(SWMS_MEDIA_USER_NAME,
SWMS_MEDIA_USER_PASSWORD,
None,
SWMS_MEDIA_FILER_PATH)

rmtmnt.mounted_path

doc = SWMSDocument.from_filer_file_name(rmtmnt, '9312122.DOCX')

doc.document.docx_obj.paragraphs