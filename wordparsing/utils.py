from pathlib import Path
import shutil
import os

def count_files(path, max=100):
    path = path if type(path) == "Path" else Path(path)
    return sum(1 for idx, _ in enumerate(path.iterdir()) if idx < max)

def count_files_fast(path):
    path = path if type(path) == "Path" else Path(path)
    return sum(1 for _ in os.scandir(path))

def rm_dir(path):
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
        return True 
    else:
        return False