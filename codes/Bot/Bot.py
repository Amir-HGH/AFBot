print("\n \n start \n \n ")

print("\n \n importing \n \n ")


# imports ________________________________________

from Codes.Api_Connection.Connection import Base_Model
from Codes.Conversation_M.Conversation_Manager import Conversation_Manager
from Codes.DataBase.DatabaseClass import Database_app
from Codes.Graph.Graph import tools_list,Build_Graph,prompt
from Codes.Log_Config.Configuration import Configuration_logging
from Codes.Login.Login import Login
from Codes.Wrapper.Runner import Runner
from Keys.Reading_Keys import Reading_Keys

# ________________________________________

import asyncio

from telegram.ext import (
    Application , MessageHandler , filters , ContextTypes
)

import logging


print("\n \n finish import \n \n ")

print("\n \n objs  \n \n ")


# build objs ________________________________________


Configuration_logging()

graph_builder = Build_Graph(
    prompt,
    tools_list,
    Base_Model
)
Graph = graph_builder.build_graph()
if Graph == False : raise RuntimeError("Graph failed")

Main_Runner = Runner(
    Graph,
    "invoke"
)
summarizer_runner = Runner(
    Base_Model,
    "invoke"
)

C_M = Conversation_Manager(
    Main_Runner,
    Database_app,
    summarizer_runner
)

login = Login(Database_app)
C_H = login.build_ch()
if C_H == False : raise RuntimeError("conversation handler failed")


print("\n \n finish objc \n \n ")


# This file ________________________________________


print("\n \n This file \n \n ")


token_reader = Reading_Keys(r"D:\Files\Pythone\AFilm Bot\Keys\Bot_Token.txt")
Token = token_reader.Read()

async def shutdown (app) : 

    Database_app.close()
    print("\n \n Finish \n \n ")

Bot = Application.builder().token(Token).post_shutdown(shutdown).build()


async def message_h (update,context : ContextTypes.DEFAULT_TYPE) : 

    result = await asyncio.to_thread ( 
        C_M.conversation_manager ,
        update.message.text ,
        context.user_data["conversation_id"] ,
        context.user_data["username"]
    )

    if result == False : 

        return await update.effective_message.reply_text(
            "درخواست شما با مشکل مواجه شد . لطفا پس از چند لحظه صبر دوباره تلاش کنید "
        )

    return await update.effective_message.reply_text(result)


Bot.add_handler(C_H)
Bot.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND,message_h)
)

Bot.run_polling()

