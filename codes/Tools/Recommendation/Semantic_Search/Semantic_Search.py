import logging
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pathlib import Path


logger = logging.getLogger(__name__)


try :

    INDEX_PATH = Path(
        r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Semantic_Search\Index\Index.index"
    )
    Index = faiss.read_index(str(INDEX_PATH))

except Exception :

    logger.exception("load index")
    raise


class Semantic_Search : 

    def __init__(self,output_number : int,user_seens:set,database):
        
        self.database = database
        self.output_number = output_number + len(user_seens)
        self.Model = None
        self.user_seens = user_seens


    # Main task  _____________________

    def load_model(self,path) :

        try : 

            model_path = Path(path)

            if model_path.is_dir() : self.Model = SentenceTransformer(str(model_path))
            else : 

                logger.error("load_model : path is not true")
                return False
            
            if self.Model : return True 
            else : 

                logger.error("load model : model is not ")
                return False

        except Exception : 

            logger.exception("load model")
            return False

    
    def embeding(self,user_sentence : str) : 

        if not self.Model : 
            
            logger.error("embeding : model is not ready")
            return False

        try:
            
            user_vector = self.Model.encode(user_sentence)

            if user_vector.size > 0 : 
                
                user_vector = self.vector_cooking(user_vector)
                return user_vector
            
            else : 

                logger.error ("embeding : user vector")
                return False

        except Exception : 

            logger.exception("embeding")
            return False


    def Semantic_Search (self,vector) :

        if vector is False or vector is None : 

            logger.error("semantic search : vector is not ")
            return False

        try :

            print("\n\nInput Vector Shape:", vector.shape)
            print("\n\nFAISS Index Dimension:", Index.d)
            print("\n\nFAISS Index Total Vectors:", Index.ntotal)

            scores, ids = Index.search(vector, self.output_number)
            ids = list(ids[0][ids[0] != -1])

            if not ids : 

                logger.error("semantic search : ids is not")
                return False

            ids = [
                movie_id for movie_id in ids if movie_id not in self.user_seens
            ]

            top_ones_ids = list(ids[:2])
            all_movie_ids = list(ids)

        except Exception : 

            logger.exception("semantic search")
            return False

        all_movies = self.return_movie_data(all_movie_ids)
        if all_movies is False : return False

        top_ones = self.return_movie_data(top_ones_ids)
        if top_ones is False : return False

        return {"success" : True , "top_ones" : top_ones , "all_movies" : all_movies}


    #  Index _____________________

    def build_index (self,dimension,number) :

        try :

            index = faiss.IndexIDMap2(
                faiss.IndexHNSWFlat(
                    dimension,
                    number,
                    faiss.METRIC_INNER_PRODUCT
                )
            )

            if not index : 

                logger.error ("build index : index is not ")
                return False

            return index

        except Exception : 

            logger.exception("build index")
            return False


    def add_index (self,index,vectors,ids) : 
        
        try : 

            ids = np.asarray(ids, dtype=np.int64)
            index.add_with_ids(vectors, ids)

        except Exception : 

            logger.exception("add index")
            return False

        return True 


    # Helpers _____________________
    
    def return_movie_data (self,movie_ids) :

        logger.info("Semantic Search IDs count: %d", len(movie_ids))
        logger.info("Semantic Search IDs sample: %s", movie_ids[:10])

        data = self.database.get_data_c (
            "movie",
            [
                "title",
                "overview",
                "genres",
                "original_language",
                "original_title" ,
                "release_date",
                "runtime",
                "tagline",
                "vote_average",
                "vote_count" ,
                "adult" ,
                "belongs_to_collection" ,
                "status" ,
                "production_countries" ,
                "spoken_languages" ,
                "id",
                "popularity"
            ],
            ["id"],
            [movie_ids]
        )

        if data is False : return False
        else : return [{
            "title" : data1[0] ,
            "overview" : data1[1] ,
            "genres" : data1[2] ,
            "original_language" : data1[3] ,
            "original_title" : data1[4] ,
            "release_date" : data1[5] ,
            "runtime" : data1[6] ,
            "tagline" : data1[7] ,
            "vote_average" : data1[8] ,
            "vote_count" : data1[9] ,
            "adult" : data1[10] ,
            "belongs_to_collection" : data1[11] ,
            "status" : data1[12] ,
            "production_countries" : data1[13] ,
            "spoken_languages" : data1[14] ,
            "id" : data1[15],
            "popularity": data1[16] }
            for data1 in data ]
      

    def vector_cooking(self,vector) :

        try :

            vector = np.array(
                vector ,
                dtype=np.float32
            )
            
            if vector.size == 0 : 

                logger.error("vectore cooking : input vector is not")
                return False
            
            vector = vector.reshape(1,-1)
            faiss.normalize_L2(vector)

        except Exception : 

            logger.exception("vector cooking ")
            return False

        return vector 


