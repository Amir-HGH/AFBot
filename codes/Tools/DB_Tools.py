from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.tools import tool 
from Codes.DataBase.DatabaseClass import Database


# { "success" , "data" } is format for export data from tools 


app = Database(
    host = "localhost" , 
    user = "python_user" , 
    password = "@iA@q3"  ,
    port = 3306 ,
    database = "afilm_bot"
)


# tools for get data __________________________________________

@tool
def get_user_profile(username : Annotated[str,InjectedState("username")]) : 

    """
        Retrieve the current user's profile and preferences from the database.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Use this tool when you need to know the user's stored interests, preferences,
        or profile before making a recommendation or deciding how to interact with
        the user.

        If the returned user profile is shorter than 50 characters, treat the
        profile as insufficient for reliable personalization. In this situation,
        ask the user about their movie and series interests, preferences, favorite
        genres, disliked genres, preferred languages, or similar preferences.
        After obtaining useful information from the user, update the profile using
        the update_user_profile tool.

        Do not invent missing user preferences and do not assume preferences that
        are not present in the stored profile.

        Returns:
            {
                "success": True,
                "data": {
                    "user_profile": str
                }
            }

            If the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    data = app.get_data_c("users",["user_profile"],["username"],[[username]])

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : { "user_profile" :data[0][0] } }
        


@tool 
def get_before_conversations_summaries(username : Annotated[str,InjectedState("username")]) :

    """
        Retrieve the summaries of the user's previous conversations.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Use this tool when previous conversation history or long-term context is
        needed and the current conversation context is not sufficient.

        The returned summaries represent previous conversations and can be used to
        understand the user's historical interests, preferences, or previous
        discussions.

        Do not treat previous conversation summaries as the user's current message
        or as guaranteed current preferences. Use them as historical context.

        Returns:
            {
                "success": True,
                "data": {
                    "before_conversations_summaries": list[str]
                }
            }

            If the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
 
    data = app.get_data_c("conversations",["summary"],["username"],[[username]])

    if data is False : return {"success" : False , "data" : None}
    else : return {
        "success" : True , 
        "data" : {
            "before_conversations_summaries" : [ s[0] for s in data ]
        }}


@tool 
def get_N_before_conversation_summary(
    number:int,
    username : Annotated[str,InjectedState("username")],
    conversation_id : Annotated[int,InjectedState("conversation_id")]
    ) :

    """
        Retrieve the summary of a specific previous conversation relative to the
        current conversation.

        The username and current conversation_id are injected automatically from
        the application state and must not be provided or inferred by the model.

        Args:
            number: The number of conversations to move backward from the current
                conversation. For example, number=1 requests the immediately
                previous conversation.

        Use this tool when you need the summary of a specific earlier conversation
        rather than all previous conversation summaries.

        The number must be a positive integer.

        Returns:
            {
                "success": True,
                "data": {
                    "1befor_conversations_summaries": str
                }
            }

            If the database operation fails or the requested conversation does not
            exist:
            {
                "success": False,
                "data": None
            }
        """

    if number <= 0:
        return {
            "success": False, 
            "data": None , 
            "message" : "The 'number' argument must be a positive integer greater than 0. The provided value is invalid. Please provide a valid positive number." 
        }
    
    target_conversation_id = conversation_id - number

    if target_conversation_id < 1:
        return {
            "success": False, 
            "data": None ,
            "message": "The requested previous conversation does not exist. The specified number goes beyond the user's available previous conversations. Please request a smaller number."
        }

    data = app.get_data_c(
    "conversations",
    ["summary"],
    ["username" , "user_conversation_id"],
    [[username],[target_conversation_id]]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : {"N_before_conversation_summary" : data[0][0] } }


@tool
def get_movie_data (movie_name:str) : 

    """
        Retrieve detailed information about a movie from the movie database.

        Use this tool when you need reliable database information about a specific
        movie, especially when the user mentions a movie by name and you need to
        verify or inspect its information.

        Args:
            movie_name: The original title of the movie to search for. Provide the
                movie name as accurately as possible based on the user's message.

        Do not invent movie information when this tool can be used to retrieve it.

        Returns:
            {
                "success": True,
                "data": {
                    "id": int,
                    "title": str,
                    "overview": str,
                    "genres": ...,
                    "original_language": str,
                    "release_date": ...,
                    "runtime": ...,
                    "tagline": ...,
                    "vote_average": ...,
                    "vote_count": ...,
                    "adult": ...,
                    "belongs_to_collection": ...,
                    "status": ...,
                    "production_countries": ...,
                    "spoken_languages": ...
                }
            }

            If the movie cannot be found or the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    data = app.get_data_c (
        "movie",
        [
            "id",
            "title",
            "overview",
            "genres",
            "original_language",
            "release_date",
            "runtime",
            "tagline",
            "vote_average",
            "vote_count" ,
            "adult" ,
            "belongs_to_collection" ,
            "status" ,
            "production_countries" ,
            "spoken_languages" 
        ],
        ["original_title"],
        [[movie_name]]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : {
        "id" : data[0][0] ,
        "title" : data[0][1] ,
        "overview" : data[0][2] ,
        "genres" : data[0][3] ,
        "original_language" : data[0][4] ,
        "release_date" : data[0][5] ,
        "runtime" : data[0][6] ,
        "tagline" : data[0][7] ,
        "vote_average" : data[0][8] ,
        "vote_count"  : data[0][9] ,
        "adult"  : data[0][10] ,
        "belongs_to_collection"  : data[0][11] ,
        "status"  : data[0][12] ,
        "production_countries"  : data[0][13] ,
        "spoken_languages"  : data[0][14] ,
    }}


# interaction weight 1
@tool
def get_user_likes (username : Annotated[str,InjectedState("username")]) :
    
    """
        Retrieve the movies that the current user has explicitly liked.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Use this tool when you need to understand which movies the user has liked
        in order to personalize recommendations or analyze the user's preferences.

        The returned movies contain relevant movie information that can be used to
        infer the user's preferences.

        Do not assume that a movie is liked unless it is returned by this tool.

        Returns:
            {
                "success": True,
                "data": {
                    "movies": [
                        {
                            "title": ...,
                            "overview": ...,
                            "genres": ...,
                            ...
                        }
                    ]
                }
            }

            If the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    movie_ids = app.get_data_c (
        "interactions",
        ["movie_id"],
        ["username","interaction"] ,
        [[username],[1]]
    )

    if movie_ids is False : return {"success" : False , "data" : None}
    
    movie_ids = [movie_id[0] for movie_id in movie_ids]

    data = app.get_data_c (
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
            "spoken_languages" 
        ],
        ["id"],
        [movie_ids]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : {"movies" : [{
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
        "spoken_languages" : data1[14] }
        for data1 in data ]
    }}


# interaction weight 2
@tool
def get_user_dislikes (username : Annotated[str,InjectedState("username")]) :
    
    """
        Retrieve the movies that the current user has explicitly disliked.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Use this tool when you need to identify movies or movie characteristics
        that the user does not prefer, especially when filtering or personalizing
        recommendations.

        Do not recommend a movie solely because it is similar to a disliked movie.
        Use the returned information as negative preference evidence.

        Returns:
            {
                "success": True,
                "data": {
                    "movies": [
                        {
                            "title": ...,
                            "overview": ...,
                            "genres": ...,
                            ...
                        }
                    ]
                }
            }

            If the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    movie_ids = app.get_data_c (
        "interactions",
        ["movie_id"],
        ["username","interaction"] ,
        [[username],[2]]
    )

    if movie_ids is False : return {"success" : False , "data" : None}
    
    movie_ids = [movie_id[0] for movie_id in movie_ids]

    data = app.get_data_c (
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
            "spoken_languages" 
        ],
        ["id"],
        [movie_ids]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : {"movies" : [{
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
        "spoken_languages" : data1[14] }
        for data1 in data ]
    }}


# interaction weight 3
@tool
def get_user_seens (username : Annotated[str,InjectedState("username")]) :
    
    """
        Retrieve the movies that the current user has marked as watched.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Use this tool when you need to know which movies the user has already seen,
        especially to avoid recommending movies that the user has already watched.

        A watched movie should not automatically be interpreted as a liked or
        disliked movie. It only indicates that the user has seen it.

        Returns:
            {
                "success": True,
                "data": {
                    "movies": [
                        {
                            "title": ...,
                            "overview": ...,
                            "genres": ...,
                            ...
                        }
                    ]
                }
            }

            If the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    movie_ids = app.get_data_c (
        "interactions",
        ["movie_id"],
        ["username","interaction"] ,
        [[username],[3]]
    )

    if movie_ids is False : return {"success" : False , "data" : None}
    
    movie_ids = [movie_id[0] for movie_id in movie_ids]

    data = app.get_data_c (
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
            "spoken_languages" 
        ],
        ["id"],
        [movie_ids]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : {"movies" : [{
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
        "spoken_languages" : data1[14] }
        for data1 in data ]
    }}


# tools for give data ________________________________________

@tool
def update_user_profile (user_profile : str , username : Annotated[str,InjectedState("username")]) : 
    
    """
        Update the current user's stored profile and preferences.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Args:
            user_profile: A concise but useful description of the user's movie and
                series preferences, interests, favorite genres, disliked genres,
                preferred languages, styles, or other relevant entertainment
                preferences.

        Use this tool after obtaining meaningful preference information from the
        user, especially when the existing profile is missing, too short, or
        outdated.

        Do not add preferences that the user did not explicitly state or that
        cannot be reasonably inferred from reliable interaction data.

        Returns:
            {
                "success": True,
                "data": None
            }

            If the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    data = app.give_data_c("users",["user_profile"],["username"],[[username]],[user_profile])

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : None}


# interaction weight 1
@tool
def like_interaction (movie_name : str , username : Annotated[str,InjectedState("username")]) :

    """
        Record that the current user liked a specific movie.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Args:
            movie_name: The original title of the movie that the user liked.

        Use this tool when the user explicitly indicates that they like or liked
        the specified movie.

        The movie name is resolved against the movie database before the interaction
        is stored. Do not invent or guess a movie identifier.

        Returns:
            {
                "success": True,
                "data": None
            }

            If the movie cannot be found or the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    movie_id = app.get_data_c("movie",["id"],["original_title"],[[movie_name]])

    if movie_id is False : return {"success" : False , "data" : None}

    movie_id = movie_id[0][0]
            
    data = app.give_data(
        "interactions",
        ["username","movie_id","interaction"],
        [username,movie_id,1]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : None}


# interaction weight 2
@tool
def dislike_interaction (movie_name : str , username : Annotated[str,InjectedState("username")]) :

    """
        Record that the current user disliked a specific movie.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Args:
            movie_name: The original title of the movie that the user disliked.

        Use this tool when the user explicitly indicates that they dislike or
        disliked the specified movie.

        The movie name is resolved against the movie database before the interaction
        is stored. Do not invent or guess a movie identifier.

        Returns:
            {
                "success": True,
                "data": None
            }

            If the movie cannot be found or the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    movie_id = app.get_data_c("movie",["id"],["original_title"],[[movie_name]])

    if movie_id is False : return {"success" : False , "data" : None}

    movie_id = movie_id[0][0]
            
    data = app.give_data(
        "interactions",
        ["username","movie_id","interaction"],
        [username,movie_id,2]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : None}


# interaction weight 3
@tool
def seen_interaction (movie_name : str , username : Annotated[str,InjectedState("username")]) :

    """
        Record that the current user has watched a specific movie.

        The username is injected automatically from the application state and must
        not be provided or inferred by the model.

        Args:
            movie_name: The original title of the movie that the user has watched.

        Use this tool when the user explicitly indicates that they have watched or
        seen the specified movie.

        A watched movie must not automatically be interpreted as liked or disliked.

        The movie name is resolved against the movie database before the interaction
        is stored. Do not invent or guess a movie identifier.

        Returns:
            {
                "success": True,
                "data": None
            }

            If the movie cannot be found or the database operation fails:
            {
                "success": False,
                "data": None
            }
        """
    
    movie_id = app.get_data_c("movie",["id"],["original_title"],[[movie_name]])

    if movie_id is False : return {"success" : False , "data" : None}

    movie_id = movie_id[0][0]
            
    data = app.give_data(
        "interactions",
        ["username","movie_id","interaction"],
        [username,movie_id,3]
    )

    if data is False : return {"success" : False , "data" : None}
    else : return {"success" : True , "data" : None}

