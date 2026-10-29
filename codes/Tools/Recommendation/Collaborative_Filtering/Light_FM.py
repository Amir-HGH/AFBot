import logging
from lightfm.data import Dataset
import joblib
from lightfm import LightFM
import numpy as np
from pathlib import Path


logger = logging.getLogger(__name__)


# in databse weights are 1,2,3 and here is 1 for 3(seen) and 2 for 1(like) and 
# dislike is -1 in a seprate way


class Interactions : 

    def __init__(self,output_number,database):

        self.output_number = output_number
        self.Model = None
        self.database = database


    # build methods _____________________

    def bsf_dataset (self,users,items,dataset_path) :

        if not Path(dataset_path).parent.is_dir() : 

            logger.error("bsf dataset : path is not ")
            return False

        try : 

            dataset = Dataset()
            dataset.fit(users=users,items=items)
            
            joblib.dump(dataset,dataset_path)

            return True

        except Exception : 

            logger.exception("bsf dataset")
            return False


    def interaction_matrix (self,dataset_path,matrix_path,interaction_data) : 

        if not Path(dataset_path).is_file() or not Path(matrix_path).parent.is_dir() : 

            logger.error("interaction matrix : path is not ")
            return False

        try :

            dataset = joblib.load(dataset_path)

            interactions , weights = dataset.build_interactions(interaction_data)

            joblib.dump(interactions,matrix_path)

            return interactions , weights

        except Exception : 

            logger.exception("interaction matrix")
            return False


    def bfs_model (
            self,
            interactions,
            weights,
            epochs,
            num_threads,
            model_path
    ) : 

        if not Path(model_path).parent.is_dir() : 

            logger.error("bsf model : path is not ")
            return False

        try:

            model = LightFM(loss="warp")

            model.fit(
                interactions,
                sample_weight=weights,
                epochs=epochs,
                num_threads=num_threads
            )

            joblib.dump(model,model_path)

            return True

        except Exception : 

            logger.exception("bsf model")
            return False


    # helpers methods _____________________

    def filter_dislikes (self,dislike_id_path,movie_list,scores,number) :

        if not Path(dislike_id_path).parent.is_dir() : 

            logger.error("filter dislikes : path is not ")
            return False

        try :

            dislike_id_path = set(joblib.load(dislike_id_path))

            for i,movie in enumerate(movie_list) : 
                
                if movie["id"] in dislike_id_path : 
                    scores[i] -= number 

            return scores

        except Exception : 

            logger.exception("filter dislikes")
            return False


    # main task methods _____________________


    # for load and check model for tool

    def load_model(self,model_path) :

        if not Path(model_path).is_file() : return None 

        try:

            self.Model = joblib.load(model_path)
            return True

        except Exception : 

            logger.exception("load model")
            return False


    def collaborative_filtering (self,username,movie_list,dislike_id_path,dataset_path) :

        if not self.Model : 

            logger.error("collaborative_filtering : model is not ready")
            return False
        
        if not Path(dataset_path).is_file() : 

            logger.error("collaborative_filtering : path is not ")
            return False  

        try :

            dataset = joblib.load(dataset_path)
            user_maping,h,item_maping,h2 = dataset.mapping()

            user_id = user_maping[username]
            item_ids = [item_maping[item["id"]] for item in movie_list]
            user_id = np.repeat(user_id,len(item_ids))

            scores = self.Model.predict(user_id,item_ids)

            scores = self.filter_dislikes(dislike_id_path,movie_list,scores,0.5)
            if scores is False : return False

            ranked_movies = sorted (
                zip([movie["id"] for movie in movie_list],scores),
                key=lambda x: x[1],
                reverse=True
            )

            ranked_movies = ranked_movies[:self.output_number]
            ranked_movies = [movie_id for movie_id,score in ranked_movies]

            top2 = ranked_movies[:2]
            top2 = [
                movie for movie in movie_list if movie["id"] in top2
            ]

            movie_list = [
                movie for movie in movie_list if movie["id"] in ranked_movies
            ]

            return {"success" : True,"level_tops" : top2,"movie_list" : movie_list}

        except Exception : 

            logger.exception("collaborative_filtering")
            return False

