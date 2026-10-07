from langgraph.graph import MessagesState


# state class
class State(MessagesState):

    username: str
    conversation_id: int

    