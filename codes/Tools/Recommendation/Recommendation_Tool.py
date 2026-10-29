from Codes.Tools.Recommendation.Semantic_Search.Semantic_Search import Semantic_Search
from Codes.Tools.Recommendation.Collaborative_Filtering.Light_FM import Interactions
from Codes.Tools.Recommendation.BR.Business_Rules import Business_Rules
from Codes.Tools.Recommendation.Helpers import filter_seens
from Codes.DataBase.DatabaseClass import Database_app
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Annotated


# Recommendation Tool


@tool
def Recommendation_Tool (
    input_text : str,
    username : Annotated[str,InjectedState("username")]
) : 


    """
        Recommend movies to the user based on their input, viewing history, preferences, and available movie information.

        This tool searches for movies that are semantically similar to the user's request, filters and ranks them using collaborative filtering when available, and applies business rules to produce the final recommendations.

        The tool returns between 2 and 6 candidate movies for the language model to consider.

        If the tool returns more than 3 movies, you must select exactly 3 movies from the returned candidates and recommend them to the user.

        Use the user's profile and preferences, when available, to make your selection. Consider the user's interests, previous likes, dislikes, and viewing history when choosing the most relevant movies.

        Do not recommend movies that the user has already seen or disliked when this information is available.

        If the tool returns 3 or fewer movies, recommend the available movies without selecting additional movies or inventing recommendations.

        Only recommend movies included in the tool's returned data. Do not invent movie titles, IDs, descriptions, or other movie information.

        The final response to the user must contain exactly 3 recommendations whenever at least 3 valid candidate movies are returned. If fewer than 3 valid candidates are available, recommend only the available candidates.
    """
    

    user_seens = filter_seens(Database_app,username)
    if user_seens is False : return {"success" : False,"data" : None}


    semantic_s = Semantic_Search(
        50,
        user_seens,
        Database_app
    )
    c_filter = Interactions(
        10,
        Database_app
    )
    b_rules = Business_Rules(
        2,
        ["vote_average","popularity"]
    )


    load_sm_result = semantic_s.load_model(
        r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Semantic_Search\Model\E_AllMiniLM_L6V2\Model"
    )
    if load_sm_result is False : return {"success" : False,"data" : None}

    input_text_vector = semantic_s.embeding(input_text)
    if input_text_vector is False : return {"success" : False,"data" : None}

    movie_dictionary = semantic_s.Semantic_Search(input_text_vector)
    if movie_dictionary is False : return {"success" : False,"data" : None}

    movie_list = movie_dictionary["all_movies"]
    result = movie_dictionary["top_ones"]


    load_cfm_result = c_filter.load_model(
        r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Collaborative_Filtering\Interaction_Matrix"
    )
    if load_cfm_result is False : return {"success" : False,"data" : None}

    elif load_cfm_result is True : 

        c_filterd_dictionary = c_filter.collaborative_filtering(
            username,
            movie_list,
            r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Collaborative_Filtering\Disliked_IDs",
            r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Collaborative_Filtering\Interaction_Matrix"
        )
        if c_filterd_dictionary is False : return {"success" : False,"data" : None}

        movie_list = c_filterd_dictionary["movie_list"]
        result.extend(c_filterd_dictionary["level_tops"])


    movie_list = b_rules.business_rules(movie_list)
    if movie_list is False : return {"success" : False,"data" : None}

    result.extend(movie_list)

    return {"success" : True,"data" : {"movie_list" : result } }


