from langchain_openai import ChatOpenAI
import logging
from Keys.Reading_Keys import Reading_Keys


logger = logging.getLogger(__name__)


class Model_Connection :

    def __init__(self,model_name : str,base_url : str,api_key : str):
        
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key

        self.model = None

    def connect (self) : 

        try : 

            self.model = ChatOpenAI(
            model = self.model_name ,
            base_url = self.base_url ,
            api_key = self.api_key 
            )

            return self.model

        except Exception : 

            logger.exception("connect")
            return False

    def bind_tools (self,tools_list) :

        if not self.model : 
            
            logger.error("bind tools : model is not suitable")
            return False 

        try : return self.model.bind_tools(tools_list)

        except Exception : 

            logger.exception("bind tools")
            return False


# build object __________________________________


Api_key = Reading_Keys(r"D:\Files\Pythone\AFilm Bot\Keys\API_key.txt")
Base_Url = Reading_Keys(r"D:\Files\Pythone\AFilm Bot\Keys\Base_Url.txt")


Connection_builder = Model_Connection(
    "qwen/qwen3.7-max" ,
    Base_Url.Read() ,
    Api_key.Read()
)

Base_Model = Connection_builder.connect()

if not Base_Model : logger.error("connection build fail")

