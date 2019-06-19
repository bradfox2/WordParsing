import json
from hashlib import sha256
from pathlib import Path
from queue import Queue

import click
import numpy as np
from bert_serving.client import BertClient
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE

from wordparsing.convert import Unoconv, convert
# Embed
##TODO: Clean up data structure for embedding object
from wordparsing.embed import embed_json_dumb
# Parse
### parse the docxs
from wordparsing.parse import parse_doc
#start a unoconv serivce as docker container
from wordparsing.services.unoconv import UNOCONV_URL
from wordparsing.storage import engine
from wordparsing.storage.data_classes import (Embedding, Model, Session,
                                              TextPart)
from wordparsing.utils import cos_sim, heirarchical_dict_to_flat_list

# TSNE
sess = Session(engine)
emb = sess.query(Embedding).all()[:250]
doc_array = np.array([e.vector for e in emb])
target_names = [e.uuid for e in emb]
X_embedded = TSNE(n_components=2).fit_transform(doc_array)
target_ids = range(len(target_names))
plt.figure(figsize=(6, 5))
colors = 'r', 'g', 'b', 'c', 'm', 'y', 'k', 'w', 'orange', 'purple'
for i, label in zip(target_ids, target_names):
    plt.scatter(X_embedded[i,0], X_embedded[i,1])# label=label)
plt.legend()
plt.show()

# Cos Sim
from sklearn.metrics.pairwise import cosine_similarity as cossim
cs = cossim(doc_array)

l1 = cs[15]
l1,l2 = zip(*sorted(zip(l1,target_names)))  #TODO: not working
embobj = sess.query(Embedding).filter(Embedding.uuid.in_((l2[:2]))).all()
epk = [e.textpart_pk for e in embobj]
[e.textpart_pk for e in sess.query(TextPart).filter(TextPart.textpart_pk.in_(epk)).all()]




