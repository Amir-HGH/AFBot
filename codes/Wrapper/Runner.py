from langchain_core.messages import HumanMessage, AIMessage


class Runner : 

    def __init__(self,model,method:str):
        self.model = model
        self.method = method


    # help method for converting the Entrance
    @staticmethod
    def converting (data):
        
        if not isinstance(data, dict):
            return data

        messages = data.get("messages")

        if not isinstance(messages, list):
            return data

        converted_messages = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                converted_messages.append(HumanMessage(content=content))

            elif role == "assistant":
                converted_messages.append(AIMessage(content=content))

            else:
                raise ValueError(f"Unsupported role: {role}")

        return {**data, "messages": converted_messages}


    # real method 
    
    def run (self,*args,convert=False,**kwargs) : 
        
        md = getattr(self.model,self.method,None)
        if md is None : return False

        if convert :
            args = tuple(self.converting(arg) for arg in args)

            kwargs = {
                key: self.converting(value)
                for key, value in kwargs.items()
            }
 
        return md(*args,**kwargs)


