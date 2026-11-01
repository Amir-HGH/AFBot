def filter_seens (database,username) : 

    user_seens = set()

    exist = database.exist(
        "interactions",
        ["movie_id"],
        ["username", "interaction"],
        [[username], [3]]
    )
    if exist == {"error" : "error"} : return False

    elif exist :

        user_seens = database.get_data_c (
            "interactions",
            ["movie_id"],
            ["username","interaction"],
            [[username],[3]]
        )
        if user_seens is False : return False
        
        user_seens = {item[0] for item in user_seens}

    return user_seens

