from pathlib import Path
import shutil
import os
import numpy as np

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

def heirarchical_dict_to_flat_list(d, txt):
    if type(d) is str:
        txt.append(d)
        return
    for k,v in d.items():
        txt.append(k)
        if type(v) is dict:
            heirarchical_dict_to_flat_list(v,txt)
        elif type(v) is list:
            for i in v:
                heirarchical_dict_to_flat_list(i,txt)
        else:
            txt.append(v)
    return txt

def cos_sim(A,B):
    return np.dot(A, B) / (np.sqrt(np.dot(A,A)) * np.sqrt(np.dot(B,B)))