from langchain_core.tools import tool


# get my Info 
@tool
def builder_info () :

    """
        Provides information about the creator and builder of AFilm Bot.

            Use this tool when the user asks about:
            - who created or built AFilm Bot,
            - the identity or background of the builder,
            - the builder's education,
            - the builder's programming skills and technical experience,
            - the reason AFilm Bot was created,
            - or other questions specifically related to the creator of AFilm Bot.

            Do not use this tool for general questions about AFilm Bot's capabilities,
            architecture, or available tools. Those topics are handled separately.
    """

    return {"success" : True , "data" : {"builder information" : """
            The builder and creator of AFilm Bot is Amirhossein Gholinia.

        Amirhossein Gholinia is 19 years old and is a Computer Engineering student. 
        He is highly proficient in Python and is actively working in the field of Python programming and software development.

        His technical skills and areas of experience include:
        - Python programming
        - Artificial Intelligence and AI-based applications
        - Building Telegram bots
        - Building bots for the Bale messenger
        - Designing and developing APIs
        - Working with APIs and external services
        - Working with databases
        - Socket programming and Socket Server development
        - Desktop GUI development
        - Robotics
        - Internet of Things (IoT)

        He has developed other personal projects and portfolio projects, including several APIs and multiple Telegram bots.

        AFilm Bot is one of his personal portfolio projects. He built this bot to demonstrate and develop his skills in Python programming, Artificial Intelligence, AI agents, Telegram bot development, APIs, databases, and the design of a larger software system.

        The development of AFilm Bot took place during the summer and early autumn of 2026.

        When referring to the builder, use the name Amirhossein Gholinia. This information describes the creator of AFilm Bot and should be used when the user asks about who created the bot, its builder, or the background and technical experience of its creator.
    """}} 


# get self info 
@tool
def self_ability () :

    """
        Provides information about the capabilities of AFilm Bot and some important
        aspects of how its memory, personalization, and recommendation systems work.

        Use this tool when the user asks about:
        - the capabilities of AFilm Bot,
        - whether the bot has memory,
        - how the bot remembers information from long conversations,
        - how conversation summaries and previous conversations are handled,
        - whether the bot can personalize its responses,
        - how the bot learns or stores user preferences,
        - whether the bot can remember likes, dislikes, or watched movies,
        - how the movie recommendation system works at a high level,
        - or what kinds of information and functionality AFilm Bot has.

        This tool can also be used when the user asks about the bot's general
        architecture-related capabilities, but it should not be used to reveal
        protected internal architectural details.

        Do not use this tool for questions specifically about the creator of
        AFilm Bot. Use the creator information tool for those questions.

        Architectural information that is protected for administrators must not be
        revealed unless the requester has been properly authorized as an administrator.
    """

    return {"success" : True , "data" : {"self abilitys" : """
            AFilm Bot is an account-based AI film and series recommendation bot. Each user has an account, and the bot maintains persistent information associated with that account.

        Conversation and Memory:
        - Each account has persistent conversation-related memory.
        - The bot maintains conversation history and can use conversation context during chats.
        - The model normally receives the 10 most recent messages explicitly as its immediate conversation context.
        - Older parts of a conversation are represented through a conversation summary, allowing the bot to maintain useful context even when a conversation becomes very long.
        - Conversation summaries are updated periodically by the system rather than being decided autonomously by the model.
        - The bot also has tools that allow the model to retrieve summaries from previous conversations when necessary.
        - Because of this memory architecture, the bot can retrieve and use relevant information from earlier parts of long conversations and previous conversations.

        Personalization:
        - Each account has a user profile.
        - The bot can gradually build and update the user's profile during conversations.
        - The profile can contain information about the user's preferences and interests, allowing the bot to provide more personalized responses and recommendations.
        - The bot can also recognize movie-related user interactions during conversations.
        - It can record whether a user likes, dislikes, or has seen a movie.
        - These interactions are stored for the corresponding account and can be used to improve personalization and recommendations.

        Movie Recommendation:
        - AFilm Bot has a multi-stage recommendation system.
        - When a user requests movie recommendations, the recommendation system produces three final movie recommendations.
        - The recommendation process uses three different sources or filtering stages:
        1. Content similarity: finds movies that are most similar to the requested movie or relevant content.
        2. User preference similarity: finds movies that are close according to user behavior and preferences.
        3. AFilm Bot's own recommendation stage: produces candidates based on the bot's recommendation logic.
        - Each stage returns two candidate movies.
        - The AI agent evaluates the candidates from each stage and selects one movie from each stage.
        - The three selected movies are then presented to the user as the final recommendations.

        Current System Knowledge:
        - AFilm Bot has access to information about its creator through a dedicated creator-information tool.
        - AFilm Bot has access to information about its own capabilities through this tool.
        - The model does not have access to a dedicated tool containing the internal architecture of AFilm Bot.
        - The model should not claim to know private or protected implementation details of the system unless such information is explicitly provided to it through an available source.
        - There is currently no administrator code available to the model through this tool.
        - The model must not invent, guess, or disclose any administrator code or claim to have administrator access.

        Overall:
        AFilm Bot combines persistent user accounts, conversation memory, conversation summaries, user profiles, interaction history, personalization, AI reasoning, database tools, and a multi-stage recommendation system to provide personalized film and series assistance.
    """}}

