print("\n \n import start \n \n ")

from Codes.DataBase.DatabaseClass import B_Database_app
from Codes.Tools.Recommendation.Semantic_Search.Semantic_Search import Semantic_Search
from Codes.Log_Config.Configuration import Configuration_logging

import json
import faiss
import numpy as np


print ("\n \n import finish \n \n ")


Configuration_logging()


semantic_searcher = Semantic_Search(
    1,
    {1,2,3},
    B_Database_app
)


print ("\n \n buil obj finish \n \n ")



id_vectors = B_Database_app.get_data(
    "movie",
    ["id","overview_vector"]
)

print ("\n \n database finish \n \n ")

if id_vectors == False : raise RuntimeError(" \n \n Error in database \n \n ")

print ("\n \n database finish 2 \n \n ")

ids = [
    id_v[0] for id_v in id_vectors
]

vectors = []

for id_v in id_vectors : 

    result = semantic_searcher.vector_cooking(json.loads(id_v[1]))
    if result is False : raise RuntimeError(" \n \n Error in vector cooking \n \n ")

    vectors.append(result)

vectors = np.vstack(vectors)


dimension = vectors.shape[1]


print ("\n \n index build start \n \n ")


Index = semantic_searcher.build_index(dimension,32)
if Index is False : raise RuntimeError(" \n \n Error in index b \n \n ")

result = semantic_searcher.add_index(Index,vectors,ids)
if result is False : raise RuntimeError(" \n \n Error in index add \n \n ")


faiss.write_index(
    Index,
    r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Semantic_Search\Index\Index.index"
)


print ("\n \n index build finish \n \n ")

