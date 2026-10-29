from Codes.Tools.Recommendation.Recommendation_Tool import Recommendation_Tool
from Codes.Tools.DB_Tools import *
from Codes.Tools.Information_Tools import *
from Codes.Graph.State import State
from langchain_core.messages import SystemMessage
from langgraph.graph import START , StateGraph  
from langgraph.prebuilt import ToolNode , tools_condition
import logging


logger = logging.getLogger(__name__)


tools_list = [
    Recommendation_Tool,
    get_user_profile,
    get_before_conversations_summaries,
    get_N_before_conversation_summary,
    get_movie_data,
    get_user_likes,
    get_user_dislikes,
    get_user_seens,
    update_user_profile,
    like_interaction,
    dislike_interaction,
    seen_interaction,
    builder_info,
    self_ability
]


prompt = """


"""


class Build_Graph :

    def __init__(self,prompt,tools_list,base_model):

        self.prompt = prompt
        self.tools_list = tools_list
        self.base_model = base_model

    def node_f (self,model) :

        def node (state) : 

            try :

                result = model.invoke([
                    SystemMessage(content=self.prompt),
                    *state["messages"]
                ])

                return {"messages" : [result]}

            except Exception :  logger.exception("node")
        
        return node
        

    # Main task __________________________________________ 
    
    def build_graph (self) :

        Model = self.base_model.bind_tools(self.tools_list)
        if Model is False : return False

        try : 

            c_node = self.node_f(Model)
            t_node = ToolNode(self.tools_list)


            graph = StateGraph(State)

            graph.add_node("chat_node",c_node)
            graph.add_node("tools",t_node)

            graph.add_edge(START,"chat_node")
            graph.add_conditional_edges("chat_node",tools_condition)
            graph.add_edge("tools","chat_node")

            graph = graph.compile()

            return graph

        except Exception : 

            logger.exception("build graph")
            return False 

        

