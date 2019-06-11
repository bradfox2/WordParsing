from pathlib import Path
import shutil

def count_files(path):
    path = path if type(path) == "Path" else Path(path)
    return sum(1 for _ in path.iterdir())

def rm_dir(path):
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
        return True 
    else:
        return False