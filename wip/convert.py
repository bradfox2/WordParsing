import os
import re
from pathlib import Path

import win32com.client as win32
from win32com.client import constants
import platform
import click

def check_os():
    return "win" if platform.system() == 'Windows' else 'nix'

@click.command()
@click.option('--path', help='Path to file for conversion.')
# Create list of paths to .doc files
def save_as_docx(path):
    if check_os() == 'Windows':
        #path = Path(path).glob('**\\7787538.doc')

        # Opening MS Word
        word = win32.gencache.EnsureDispatch('Word.Application')
        doc = word.Documents.Open(path)
        doc.Activate ()

        # Rename path with .docx
        new_file_abs = os.path.abspath(path)
        new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

        # Save and Close
        word.ActiveDocument.SaveAs(
            new_file_abs, FileFormat=constants.wdFormatXMLDocument
        )
        doc.Close(False)

        return new_file_abs
    else:
        pass
        
if __name__ == "__main__":
    save_as_docx()
